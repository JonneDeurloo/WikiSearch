import sys
import os
import re
import csv
import math
import json
import string
import unidecode

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from ..dbmanager import dbmanager as DBM

#from ..common.article import Article

# GLOBAL VARIABLES
file_articles = "articles_in_plain_text.txt"
file_titles = "article_titles.txt"


def create_connection():
    """ Create a database connection to an SQLite database """

    global db
    db = DBM.create_connection('wiki')


def create_table_indexing():
    """ Create wiki table (if not exists) """

    cursor = db.cursor()
    cursor.execute(
        '''DROP TABLE IF EXISTS `indexing`''')
    cursor.execute(
        '''
		CREATE TABLE IF NOT EXISTS indexing(
			id 			INTEGER PRIMARY KEY,
			term 		TEXT unique,
			counter 	INTEGER,
            indexes     TEXT)
	    ''')
    db.commit()


def create_indexing(dataset, force=False):
    """ Build the indexing table """

    if force or not DBM.table_exists(db, 'indexing'):
        create_table_indexing()

        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(dir_path, f'..\\common\\dataset\\{dataset}')

        path_articles = file_path + f'\\{file_articles}'
        path_titles = file_path + f'\\{file_titles}'

        inv_index_list = indexdict_to_string(
            index_articles(path_articles, path_titles))

        cursor = db.cursor()
        cursor.executemany(
            '''INSERT INTO indexing(term, counter, indexes) VALUES(?, ?, ?)''', inv_index_list)
        db.commit()
    else:
        return


def get_all_from_indexing():
    """ Get all values from the indexing table """

    cursor = db.cursor()
    cursor.execute('''SELECT term, counter, indexes FROM indexing''')
    return cursor.fetchall()


def get_from_indexing(value):
    """ Get all values from the indexing table """

    cursor = db.cursor()
    cursor.execute(
        f"SELECT term, counter, indexes FROM indexing WHERE term='{value}'")
    return cursor.fetchall()


def index_articles(article_text, article_title):
    """ Return an inverted index based on articles. """

    index_dict = {}
    articles = article_list(article_text)
    #titles = article_title_list(article_title)
    # for counter, title in enumerate(titles):
    #    print('Doing new title', counter, '...')
    #    for token in title:
    #        if token not in index_dict:
    #            index_dict[token] = [1, {}]
    #            index_dict[token][1][counter] = 1
    #        else:
    #            index_dict[token][0] += 1
    #            if counter in index_dict[token][1]:
    #                index_dict[token][1][counter] += 1
    #            else:
    #                index_dict[token][1][counter] = 1
    for counter, art in enumerate(articles):
        if counter % 100 == 0:
            print('Doing new article', counter, '...')

        tokens = tokenize_article2(art)
        for token in tokens:
            if token not in index_dict:
                index_dict[token] = [1, {}]
                index_dict[token][1][counter] = 1
            else:
                index_dict[token][0] += 1
                if counter in index_dict[token][1]:
                    index_dict[token][1][counter] += 1
                else:
                    index_dict[token][1][counter] = 1

    return index_dict


def indexdict_to_string(mydict):
    """ Return a dictionary as a list of strings representations of each entry. """

    inv_index_list = []
    for k1, v1 in mydict.items():
        index_string = ''
        for k2, v2 in mydict[k1][1].items():
            temp = "{}:{} ".format(k2, v2)
            index_string += temp
        index_string = index_string[:-1]
        mydict[k1][1] = index_string

        inv_index_list.append([k1, v1[0], v1[1]])

    return inv_index_list


def article_list(file):
    """ Split text file into a list of articles. """

    articles = []
    # read the file
    with open(file, 'r', encoding="utf8") as tf:
        index = 0
        # read each line
        for line in tf:
            # delete enters and tabs
            line = line.replace('\n', ' ').replace('\t', ' ')
            # split the text into the first word and the rest
            split = line.split(' ', 1)
            # check if it is a new article
            if split[0] == '#Article:':
                # if so add it so a new element in the list and update the index
                articles.append(split[1])
                index += 1
            # else if whitelines or (sub)titles don't check but continue
            elif line == ' ' or line[0] == '#':
                continue
            # else add the line to the current element in the list
            else:
                articles[index-1] += line

    # return all the articles
    return articles


def tokenize_title(string):
    """ Returns a list of tokens based on the title of an article. """

    string = string.replace('\n', '')
    #print('Original:     ', string)
    string = string.lower()
    string = change_utf_to_ascii(string)
    #print('Lowering:     ', string)
    string = string.replace('-', ' ')
    #print('- Replacement:', string)
    string = string.replace('\'', '')
    #print('\' Removal:    ', string)
    #string = string.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))
    #print('Punctuation:  ', string)
    token_string = word_tokenize(string)
    #token_string = string.split(' ')
    #print('Tokenizing:   ', token_string)

    stop_words = stopwords.words('english')
    token_stop = [word for word in token_string
                  if word not in stop_words and check_viable_word(word)]
    if len(token_stop) == 0:
        token_stop = token_string

    #print('Stop-words:   ', token_stop)
    ps = PorterStemmer()
    token_stem = [ps.stem(word) for word in token_stop]

    return token_stem


def tokenize_article2(art_text):
    """ Returns a list of tokens where each element is lowered, stripped from punctuation and stopwords, and stemmed. """

    #print('Original:     ', art_text)
    art_text = art_text.lower()
    #print('Lowering:     ', art_text)
    art_text = change_utf_to_ascii(art_text)
    #print('\' Removal:    ', art_text)
    art_text = art_text.translate(str.maketrans(
        string.punctuation, ' '*len(string.punctuation)))
    #print('Punctuation:  ', art_text)
    sorted_tokens = sorted(word_tokenize(art_text))
    #token_art_text = art_text.split(' ')
    #print('Tokenizing:   ', token_art_text)

    stop_words = stopwords.words('english')
    ps = PorterStemmer()
    tokens_art_text = [ps.stem(word) for word in sorted_tokens
                       if word not in stop_words and check_viable_word(word)]

    # return the tokenized article
    return tokens_art_text


def change_utf_to_ascii(text):
    """ Return the ASCII version of utf-8 text. """

    res = ''
    for i in range(len(text)):
        try:
            c = text[i]
            s = unidecode.unidecode(c)
            s = s.encode(encoding='utf-8').decode('ascii')
            s = s.lower()
            if (c == '.' or c == ',') and (text[i-1].isdigit() and text[i+1].isdigit()):
                s = s
            elif s in '\'':
                s = ''
            elif s in string.punctuation:
                s = ' '
        except UnicodeDecodeError:
            s = ' '
        res += s

    return res


def check_viable_word(word):
    """ Check if a word contains at least one letter or digit """

    return re.search("\\d|[a-z]", word) != None


# Never used?
def document_vectors(mydict):
    print(len(mydict.items()))

    doc_vecs = []
    for i in range(13385):
        doc_vec = []
        for term, freq_docs in mydict.items():
            docs_counts = freq_docs[1]
            doc_freq = len(docs_counts)
            tf_log = 0
            if i in docs_counts.keys():
                doc_count = docs_counts[i]
                tf_log = 1 + math.log10(doc_count)

            idf_term = math.log10(float(13385) / float(doc_freq))
            doc_vec.append(tf_log * idf_term)

        doc_vecs.append(doc_vec)

    return doc_vecs


# Never used?
def article_title_list(file):
    """ Return list with all article titles. """

    titles = []

    # read the file
    with open(file, 'r', encoding="utf8") as tf:
        # index = 0
        # read each line
        for line in tf:
            tokens = tokenize_title(line)
            titles.append(tokens)
            # newline = line.replace('\n', '')
            # newline = newline.lower()
            # newline = newline.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))
            # newline_split = newline.split(' ')
            #
            # ps = PorterStemmer()
            # newline_stemmed = [ps.stem(word) for word in newline_split if word != '']
            #
            # titles.append(newline_stemmed)

    # return all the titles
    return titles


#article = "Constantine, son of Áed (Medieval Gaelic: Constantín mac Áeda; Modern Gaelic: Còiseam mac Aoidh, known in most modern regnal lists as Constantine II; born no later than 879; died 952) was an early King of Scotland, known then by the Gaelic name Alba. The Kingdom of Alba, a name which first appears in Constantine's lifetime, was situated in modern-day Scotland. The core of the kingdom was formed by the lands around the River Tay. Its southern limit was the River Forth, northwards it extended towards the Moray Firth and perhaps to Caithness, while its western limits are uncertain. Constantine's grandfather Kenneth I of Scotland (Cináed mac Ailpín, died 858) was the first of the family recorded as a king, but as king of the Picts. This change of title, from king of the Picts to king of Alba, is part of a broader transformation of Pictland and the origins of the Kingdom of Alba are traced to Constantine's lifetime. His reign, like those of his predecessors, was dominated by the actions of Viking rulers in the British Isles, particularly the Uí Ímair (\"the grandsons of Ímar\", or Ivar the Boneless). During Constantine's reign the rulers of the southern kingdoms of Wessex and Mercia, later the Kingdom of England, extended their authority northwards into the disputed kingdoms of Northumbria. At first allied with the southern rulers against the Vikings, Constantine in time came into conflict with them. King Æthelstan was successful in securing Constantine's submission in 927 and 934, but the two again fought when Constantine, allied with the Strathclyde Britons and the Viking king of Dublin, invaded Æthelstan's kingdom in 937, only to be defeated at the great battle of Brunanburh. In 943 Constantine abdicated the throne and retired to the Céli Dé (Culdee) monastery of St Andrews where he died in 952. He was succeeded by his predecessor's son Malcolm I (Máel Coluim mac Domnaill). Constantine's reign of 43 years, exceeded in Scotland only by that of King William the Lion before the Union of the Crowns in 1603, is believed to have played a defining part in the gaelicisation of Pictland, in which his patronage of the Irish Céli Dé monastic reformers was a significant factor. During his reign the words \"Scots\" and \"Scotland\" (Scottas, Scotland) are first used to mean part of what is now Scotland. The earliest evidence for the ecclesiastical and administrative institutions which would last until the Davidian Revolution also appears at this time. Compared to neighbouring Ireland and Anglo-Saxon England, few records of 9th- and 10th-century events in Scotland survive. The main local source from the period is the Chronicle of the Kings of Alba, a list of kings from Kenneth MacAlpin (died 858) to Kenneth II (Cináed mac Maíl Coluim, died 995). The list survives in the Poppleton Manuscript, a 13th-century compilation. Originally simply a list of kings with reign lengths, the other details contained in the Poppleton Manuscript version were added in the 10th and 12th centuries. In addition to this, later king lists survive. The earliest genealogical records of the descendants of Kenneth MacAlpin may date from the end of the 10th century, but their value lies more in their context, and the information they provide about the interests of those for whom they were compiled, than in the unreliable claims they contain. For narrative history the principal sources are the Anglo-Saxon Chronicle and the Irish annals. The evidence from charters created in the Kingdom of England provides occasional insight into events in northern Britain. While Scandinavian sagas describe events in 10th-century Britain, their value as sources of historical narrative, rather than documents of social history, is disputed. Mainland European sources rarely concern themselves with affairs in Britain, and even less commonly with events in northern Britain, but the life of Saint Cathróe of Metz, a work of hagiography written in Germany at the end of the 10th century, provides plausible details of the saint's early life in north Britain. While the sources for north-eastern Britain, the lands of the kingdom of Northumbria and the former Pictland, are limited and late, those for the areas on the Irish Sea and Atlantic coasts—the modern regions of north-west England and all of northern and western Scotland—are non-existent, and archaeology and toponymy are of primary importance. The dominant kingdom in eastern Scotland before the Viking Age was the northern Pictish kingdom of Fortriu on the shores of the Moray Firth. By the 9th century, the Gaels of Dál Riata (Dalriada) were subject to the kings of Fortriu of the family of Constantín mac Fergusa (Constantine son of Fergus). Constantín's family dominated Fortriu after 789 and perhaps, if Constantín was a kinsman of Óengus I of the Picts (Óengus son of Fergus), from around 730. The dominance of Fortriu came to an end in 839 with a defeat by Viking armies reported by the Annals of Ulster in which King Uen of Fortriu and his brother Bran, Constantín's nephews, together with the king of Dál Riata, Áed mac Boanta, \"and others almost innumerable\" were killed. These deaths led to a period of instability lasting a decade as several families attempted to establish their dominance in Pictland. By around 848 Kenneth MacAlpin had emerged as the winner. Later national myth made Kenneth MacAlpin the creator of the kingdom of Scotland, the founding of which was dated from 843, the year in which he was said to have destroyed the Picts and inaugurated a new era. The historical record for 9th-century Scotland is meagre, but the Irish annals and the 10th-century Chronicle of the Kings of Alba agree that Kenneth was a Pictish king, and call him \"king of the Picts\" at his death. The same style is used of Kenneth's brother Donald I (Domnall mac Ailpín) and sons Constantine I (Constantín mac Cináeda) and Áed (Áed mac Cináeda). The kingdom ruled by Kenneth's descendants—older works used the name House of Alpin to describe them but descent from Kenneth was the defining factor, Irish sources referring to Clann Cináeda meic Ailpín (\"the Clan of Kenneth MacAlpin\")—lay to the south of the previously dominant kingdom of Fortriu, centred in the lands around the River Tay. The extent of Kenneth's nameless kingdom is uncertain, but it certainly extended from the Firth of Forth in the south to the Mounth in the north. Whether it extended beyond the mountainous spine of north Britain—Druim Alban—is unclear. The core of the kingdom was similar to the old counties of Mearns, Forfar, Perth, Fife, and Kinross. Among the chief ecclesiastical centres named in the records are Dunkeld, probably seat of the bishop of the kingdom, and Cell Rígmonaid (modern St Andrews). Kenneth's son Constantine died in 876, probably killed fighting against a Viking army which had come north from Northumbria in 874. According to the king lists, he was counted the 70th and last king of the Picts in later times. In 899 Alfred the Great, king of Wessex, died leaving his son Edward the Elder as ruler of Britain south of the River Thames and his daughter Æthelflæd and son-in-law Æthelred ruling the western, English part of Mercia. The situation in the Danish kingdoms of eastern Britain is less clear. King Eohric was probably ruling in East Anglia, but no dates can reliably be assigned to the successors of Guthfrith of York in Northumbria. It is known that Guthfrith was succeeded by Sigurd and Cnut, although whether these men ruled jointly or one after the other is uncertain. Northumbria may have been divided by this time between the Viking kings in York and the local rulers, perhaps represented by Eadulf, based at Bamburgh who controlled the lands from the River Tyne or River Tees to the Forth in the north. In Ireland, Flann Sinna, married to Constantine's aunt Máel Muire, was dominant. The years around 900 represented a period of weakness among the Vikings and Norse-Gaels of Dublin. They are reported to have been divided between two rival leaders. In 894 one group left Dublin, perhaps settling on the Irish Sea coast of Britain between the River Mersey and the Firth of Clyde. The remaining Dubliners were expelled in 902 by Flann Sinna's son-in-law Cerball mac Muirecáin, and soon afterwards appeared in western and northern Britain. To the south-west of Constantine's lands lay the kingdom of Strathclyde. This extended north into the Lennox, east to the River Forth, and south into the Southern Uplands. In 900 it was probably ruled by King Dyfnwal. The situation of the Gaelic kingdoms of Dál Riata in western Scotland is uncertain. No kings are known by name after Áed mac Boanta. The Frankish Annales Bertiniani may record the conquest of the Inner Hebrides, the seaward part of Dál Riata, by Northmen in 849. In addition to these, the arrival of new groups of Vikings from northern and western Europe was still commonplace. Whether there were Viking or Norse-Gael kingdoms in the Western Isles or the Northern Isles at this time is debated. Áed, Constantine's father, succeeded Constantine's uncle and namesake Constantine I in 876 but was killed in 878. Áed's short reign is glossed as being of no importance by most king lists. Although the date of his birth is nowhere recorded, Constantine II cannot have been born any later than the year after his father's death, that is 879. His name may suggest that he was born a few years earlier, during the reign of his uncle Constantine I. After Áed's death, there is a two-decade gap until the death of Donald II (Domnall mac Constantín) in 900 during which nothing is reported in the Irish annals. The entry for the reign between Áed and Donald II is corrupt in the Chronicle of the Kings of Alba, and in this case the Chronicle is at variance with every other king list. According to the Chronicle, Áed was followed by Eochaid, a grandson of Kenneth MacAlpin, who is somehow connected with Giric, but all other lists say that Giric ruled after Áed and make great claims for him. Giric is not known to have been a kinsman of Kenneth's, although it has been suggested that he was related to him by marriage. The major changes in Pictland which began at about this time have been associated by Alex Woolf and Archie Duncan with Giric's reign. Woolf suggests that Constantine and his cousin Donald may have passed Giric's reign in exile in Ireland where their aunt Máel Muire was wife of two successive High Kings of Ireland, Áed Findliath and Flann Sinna. Giric died in 889. If he had been in exile, Constantine may have returned to Pictland where his cousin Donald II became king. Donald's reputation is suggested by the epithet dasachtach, a word used of violent madmen and mad bulls, attached to him in the 11th-century writings of Flann Mainistrech, echoed by his description in the Prophecy of Berchan as \"the rough one who will think relics and psalms of little worth\". Wars with the Viking kings in Britain and Ireland continued during Donald's reign and he was probably killed fighting yet more Vikings at Dunnottar in the Mearns in 900. Constantine succeeded him as king. The earliest event recorded in the Chronicle of the Kings of Alba in Constantine's reign is an attack by Vikings and the plundering of Dunkeld \"and all Albania\" in his third year. This is the first use of the word Albania, the Latin form of the Old Irish Alba, in the Chronicle which until then describes the lands ruled by the descendants of Cináed as Pictavia. These Northmen may have been some of those who were driven out of Dublin in 902, but could also have been the same group who had defeated Domnall in 900. The Chronicle states that the Northmen were killed in Srath Erenn, which is confirmed by the Annals of Ulster which records the death of Ímar grandson of Ímar and many others at the hands of the men of Fortriu in 904. This Ímar was the first of the Uí Ímair, that is the grandsons of Ímar, to be reported; three more grandsons of Ímar appear later in Constantín's reign. The Fragmentary Annals of Ireland contain an account of the battle, and this attributes the defeat of the Norsemen to the intercession of Saint Columba following fasting and prayer. An entry in the Chronicon Scotorum under the year 904 may possibly contain a corrupted reference to this battle. The next event reported by the Chronicle of the Kings of Alba is dated to 906. This records that:King Constantine and Bishop Cellach met at the Hill of Belief near the royal city of Scone and pledged themselves that the laws and disciplines of the faith, and the laws of churches and gospels, should be kept pariter cum Scottis. The meaning of this entry, and its significance, have been the subject of debate. The phrase pariter cum Scottis in the Latin text of the Chronicle has been translated in several ways. William Forbes Skene and Alan Orr Anderson proposed that it should be read as \"in conformity with the customs of the Gaels\", relating it to the claims in the king lists that Giric liberated the church from secular oppression and adopted Irish customs. It has been read as \"together with the Gaels\", suggesting either public participation or the presence of Gaels from the western coasts as well as the people of the east coast. Finally, it is suggested that it was the ceremony which followed \"the custom of the Gaels\" and not the agreements. The idea that this gathering agreed to uphold Irish laws governing the church has suggested that it was an important step in the gaelicisation of the lands east of Druim Alban. Others have proposed that the ceremony in some way endorsed Constantine's kingship, prefiguring later royal inaugurations at Scone. Alternatively, if Bishop Cellach was appointed by Giric, it may be that the gathering was intended to heal a rift between king and church. Following the events at Scone, there is little of substance reported for a decade. A story in the Fragmentary Annals of Ireland, perhaps referring to events some time after 911, claims that Queen Æthelflæd, who ruled in Mercia, allied with the Irish and northern rulers against the Norsemen on the Irish sea coasts of Northumbria. The Annals of Ulster record the defeat of an Irish fleet from the kingdom of Ulaid by Vikings \"on the coast of England\" at about this time. In this period the Chronicle of the Kings of Alba reports the death of Cormac mac Cuilennáin, king of Munster, in the eighth year of Constantine's reign. This is followed by an undated entry which was formerly read as \"In his time Domnall Dyfnwal, king of the Strathclyde Britons died, and Domnall son of Áed was elected\". This was thought to record the election of a brother of Constantine named Domnall to the kingship of the Britons of Strathclyde and was seen as early evidence of the domination of Strathclyde by the kings of Alba. The entry in question is now read as \"...Dynfwal... and Domnall son Áed king of Ailech died\", this Domnall being a son of Áed Findliath who died on 21 March 915. Finally, the deaths of Flann Sinna and Niall Glúndub are recorded. There are more reports of Viking fleets in the Irish Sea from 914 onwards. By 916 fleets under Sihtric Cáech and Ragnall, said to be grandsons of Ímar (that is, they belonged to the same Uí Ímair kindred as the Ímar who was killed in 904), were very active in Ireland. Sihtric inflicted a heavy defeat on the armies of Leinster and retook Dublin in 917. The following year Ragnall appears to have returned across the Irish sea intent on establishing himself as king at York. The only precisely dated event in the summer of 918 is the death of Queen Æthelflæd on 12 June 918 at Tamworth, Staffordshire. Æthelflæd had been negotiating with the Northumbrians to obtain their submission, but her death put an end to this and her successor, her brother Edward the Elder, was occupied with securing control of Mercia. The northern part of Northumbria, and perhaps the whole kingdom, had probably been ruled by Ealdred son of Eadulf since 913. Faced with Ragnall's invasion, Ealdred came north seeking assistance from Constantine. The two advanced south to face Ragnall, and this led to a battle somewhere on the banks of the River Tyne, probably at Corbridge where Dere Street crosses the river. The Battle of Corbridge appears to have been indecisive; the Chronicle of the Kings of Alba is alone in giving Constantine the victory. The report of the battle in the Annals of Ulster says that none of the kings or mormaers among the men of Alba were killed. This is the first surviving use of the word mormaer; other than the knowledge that Constantine's kingdom had its own bishop or bishops and royal villas, this is the only hint to the institutions of the kingdom. After Corbridge, Ragnall enjoyed only a short respite. In the south, Alfred's son Edward had rapidly secured control of Mercia and had a burh constructed at Bakewell in the Peak District from which his armies could easily strike north. An army from Dublin led by Ragnall's kinsman Sihtric struck at north-western Mercia in 919, but in 920 or 921 Edward met with Ragnall and other kings. The Anglo-Saxon Chronicle states that these king \"chose Edward as father and lord\". Among the other kings present were Constantine, Ealdred son of Eadwulf, and the king of Strathclyde, Owain ap Dyfnwal. Here, again, a new term appears in the record, the Anglo-Saxon Chronicle for the first time using the word scottas, from which Scots derives, to describe the inhabitants of Constantine's kingdom in its report of these events. Edward died in 924. His realms appear to have been divided with the West Saxons recognising Ælfweard while the Mercians chose Æthelstan who had been raised at Æthelflæd's court. Ælfweard died within weeks of his father and Æthelstan was inaugurated as king of all of Edward's lands in 925. By 926 Sihtric had evidently acknowledged Æthelstan as over-king, adopting Christianity and marrying a sister of Æthelstan at Tamworth. Within the year he may have abandoned his new faith and repudiated his wife, but before Æthelstan and he could fight, Sihtric died suddenly in 927. His kinsman, perhaps brother, Gofraid, who had remained as his deputy in Dublin, came from Ireland to take power in York, but failed. Æthelstan moved quickly, seizing much of Northumbria. In less than a decade, the kingdom of the English had become by far the greatest power in Britain and Ireland, perhaps stretching as far north as the Firth of Forth. John of Worcester's chronicle suggests that Æthelstan faced opposition from Constantine, from Owain, and from the Welsh kings. William of Malmesbury writes that Gofraid, together with Sihtric's young son Olaf Cuaran fled north and received refuge from Constantine, which led to war with Æthelstan. A meeting at Eamont Bridge on 12 July 927 was sealed by an agreement that Constantine, Owain, Hywel Dda, and Ealdred would \"renounce all idolatry\": that is, they would not ally with the Viking kings. William states that Æthelstan stood godfather to a son of Constantine, probably Indulf (Ildulb mac Constantín), during the conference. Æthelstan followed up his advances in the north by securing the recognition of the Welsh kings. For the next seven years, the record of events in the north is blank. Æthelstan's court was attended by the Welsh kings, but not by Constantine or Owain. This absence of record means that Æthelstan's reasons for marching north against Constantine in 934 are unclear. Æthelstan's campaign is reported by in brief by the Anglo-Saxon Chronicle, and later chroniclers such as John of Worcester, William of Malmesbury, Henry of Huntingdon, and Symeon of Durham add detail to that bald account. Æthelstan's army began gathering at Winchester by 28 May 934, and reached Nottingham by 7 June. He was accompanied by many leaders, including the Welsh kings Hywel Dda, Idwal Foel, and Morgan ab Owain. From Mercia the army went north, stopping at Chester-le-Street, before resuming the march accompanied by a fleet of ships. Owain was defeated and Symeon states that the army went as far north as Dunnottar and Fortriu, while the fleet is said to have raided Caithness, by which a much larger area, including Sutherland, is probably intended. It is unlikely that Constantine's personal authority extended so far north, and while the attacks may have been directed at his allies, they may also have been simple looting expeditions. The Annals of Clonmacnoise state that \"the Scottish men compelled Æthelstan to return without any great victory\", while Henry of Huntingdon claims that the English faced no opposition. A negotiated settlement may have ended matters: according to John of Worcester, a son of Constantine was given as a hostage to Æthelstan and Constantine himself accompanied the English king on his return south. He witnessed a charter with Æthelstan at Buckingham on 13 September 934 in which he is described as subregulus, that is a king acknowledging Æthelstan's overlordship. The following year, Constantine was again in England at Æthelstan's court, this time at Cirencester where he appears as a witness, appearing as the first of several subject kings, followed by Owain and Hywel Dda, who subscribed to the diploma. At Christmas of 935, Owain was once more at Æthelstan's court along with the Welsh kings, but Constantine was not. His return to England less than two years later would be in very different circumstances. Following his disappearance from Æthelstan's court after 935, there is no further report of Constantine until 937. In that year, together with Owain and Olaf Guthfrithson of Dublin, Constantine invaded England. The resulting battle of Brunanburh—Dún Brunde—is reported in the Annals of Ulster as follows:a great battle, lamentable and terrible was cruelly fought... in which fell uncounted thousands of the Northmen. ...And on the other side, a multitude of Saxons fell; but Æthelstan, the king of the Saxons, obtained a great victory. The battle was remembered in England a generation later as \"the Great Battle\". When reporting the battle, the Anglo-Saxon Chronicle abandons its usual terse style in favour of a heroic poem vaunting the great victory. In this the \"hoary\" Constantine, by now around 60 years of age, is said to have lost a son in the battle, a claim which the Chronicle of the Kings of Alba confirms. The Annals of Clonmacnoise give his name as Cellach. For all its fame, the site of the battle is uncertain and several sites have been advanced, with Bromborough on the Wirral the most favoured location. Brunanburh, for all that it had been a famous and bloody battle, settled nothing. On 27 October 939 Æthelstan, the \"pillar of the dignity of the western world\" in the words of the Annals of Ulster, died at Malmesbury. He was succeeded by his brother Edmund, then aged 18. Æthelstan's empire, seemingly made safe by the victory of Brunanburh, collapsed in little more than a year from his death when Amlaíb returned from Ireland and seized Northumbria and the Mercian Danelaw. Edmund spent the remainder of Constantín's reign rebuilding the empire. For Constantine's last years as king there is only the meagre record of the Chronicle of the Kings of Alba. The death of Æthelstan is reported, as are two others. The first of these, in 938, is that of Dubacan, mormaer of Angus or son of the mormaer. Unlike the report of 918, on this occasion the title mormaer is attached to a geographical area, but it is unknown whether the Angus of 938 was in any way similar to the later mormaerdom or earldom. The second death, entered with that of Æthelstan, is that of Eochaid mac Ailpín, who may, from his name, have been a kinsman of Constantín. By the early 940s Constantine was an old man in his late sixties or seventies. The kingdom of Alba was too new to be said to have a customary rule of succession, but Pictish and Irish precedents favoured an adult successor descended from Kenneth MacAlpin. Constantine's surviving son Indulf, probably baptised in 927, would have been too young to be a serious candidate for the kingship in the early 940s, and the obvious heir was Constantine's nephew, Malcolm I. As Malcolm was born no later than 901, by the 940s he was no longer a young man, and may have been impatient. Willingly or not—the 11th-century Prophecy of Berchán, a verse history in the form of a supposed prophecy, states that it was not a voluntary decision—Constantine abdicated in 943 and entered a monastery, leaving the kingdom to Malcolm. Although his retirement may have been involuntary, the Life of Cathróe of Metz and the Prophecy of Berchán portray Constantine as a devout king. The monastery which Constantine retired to, and where he is said to have been abbot, was probably that of St Andrews. This had been refounded in his reign and given to the reforming Céli Dé (Culdee) movement. The Céli Dé were subsequently to be entrusted with many monasteries throughout the kingdom of Alba until replaced in the 12th century by new orders imported from France. Seven years later the Chronicle of the Kings of Alba says:I plundered the English as far as the river Tees, and he seized a multitude of people and many herds of cattle: and the Scots called this the raid of Albidosorum, that is, Nainndisi. But others say that Constantine made this raid, asking of the king, Malcolm, that the kingship should be given to him for a week's time, so that he could visit the English. In fact, it was Malcolm who made the raid, but Constantine incited him, as I have said. Woolf suggests that the association of Constantine with the raid is a late addition, one derived from a now-lost saga or poem. Constantine's death in 952 is recorded by the Irish annals, who enter it among ecclesiastics. His son Indulf would become king on Malcolm's death. The last of Constantine's certain descendants to be king in Alba was a great-grandson, Constantine III (Constantín mac Cuiléin). Another son had died at Brunanburh, and, according to John of Worcester, Amlaíb mac Gofraid was married to a daughter of Constantine. It is possible that Constantine had other children, but like the name of his wife, or wives, this has not been recorded. The form of kingdom which appeared in Constantine's reign continued in much the same way until the Davidian Revolution in the 12th century. As with his ecclesiastical reforms, his political legacy was the creation of a new form of Scottish kingship that lasted for two centuries after his death."
#tokens = tokenize_article2(article)
#sorted = sorted(tokens)
#print('not test2:', sorted)


# letters = 'abcdefghijklmnopqrstuvwxyz'
# stop2words = stopwords.words('english')
# for c in letters:
#     if c in stop2words:
#         print(c)
#
# dic = {
#     "a": [10, {1: 5, 2: 5}],
#     "b": [20, {1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2}],
#     "c": [4,  {1: 1, 2: 2, 3: 1}]
# }
#
# doc_vecs = []
# for i in range(10):
#     if(i == 0): continue
#     print(f'======== doc {i} =========')
#     doc_vec = []
#     for term, freq_docs in dic.items():
#         print('---------')
#         print('term:    ', term)
#         print('counter: ', freq_docs[0])
#         docs_counts = freq_docs[1]
#         doc_freq = len(docs_counts)
#         print('doc_freq:', doc_freq)
#         tf_log = 0
#         if i in docs_counts.keys():
#             doc_count = docs_counts[i]
#             tf_log = 1 + math.log10(doc_count)
#         print('tf_log:  ', tf_log)
#         idf_term = math.log10(float(9) / float(doc_freq))
#         print('idf_term:', idf_term)
#         doc_vec.append(tf_log * idf_term)
#     doc_vecs.append(doc_vec)
# print(doc_vecs)


# dir_path = os.path.dirname(os.path.realpath(__file__))
# file_path = os.path.join(dir_path, f'..\\common\\dataset')
# path_titles = file_path + f'\\{file_titles}'
# path_articles = file_path + f'\\articles_in_plain_text_test.txt'
# titles = article_title_list(path_titles)
# articles = article_list(path_articles)
# document_vectors(index_articles(path_articles, path_titles))
#print('total articles, file titles:  ', len(titles))
#print('total articles, file articles:', len(articles))

#ts = article_title_list(path_titles)
# for i in range(len(ts)):
#    print(i, ":", ts[i])


# test = 'abc äáâ ç äåé®þüúíóöáßðæ©ñ   ~!@#$%^&*()_+|}{":?><,./;\'\][=` hello\'s'
# test1 = change_utf_to_ascii(test)
# print(test)
# print(test1)
#
# test2 = '~!@#$%^&*()_+|}{":?><,./;\'\][=`'
# for c in test2:
#     if c not in string.punctuation:
#         print(c)

#text = "12-year-old stereotype's: 🤓 (code point U+1F913) 25,1% 25.1% $3,99 $50.000 5,000 The Chinese abacus migrated from China to Korea around 1400 AD. Koreans call it jupan (주판), supan (수판) or jusan (주산).The four beads abacus( 1:4 ) was introduced to Korea Goryeo Dynaty from the China during Song Dynasty, later the five beads abacus (5:1) abacus was introduced to Korean from China during the Ming Dynasty."
#tokens = tokenize_article2(text)
#print('Tokens:       ', tokens)


# text = "12-year-old €80,000 ὀργασμός test hi hello ©® Mr. Smith. Hello this is a sentence."
# text2 = change_utf_to_ascii(text)
# tokens = word_tokenize(text2, 'english')
# print('Tokens:', tokens)
# tokens2 = [word for word in tokens
#                   if check_viable_word(word)]
# print('Tokens:', tokens2)

# print('\n')

#word1 = ' ----'
# for char in word1:
#     hasPunctuation = False
#     if(char in string.punctuation):
#         hasPunctuation = True
#
#     print('char:', char, hasPunctuation)
#
# print('\n')
#
# word2 = '—---'
# word2change = change_utf_to_ascii(word2)
# print('change word:', word2change)
# viable = is_english(word2change)
# print('word:', word2change, 'viable:', viable)
# word2 = '｛（'
# viable = is_english(word2change)
# print('word:', word2change, 'viable:', viable)
#
# print('\n')
#
# word3 = 'tribune—both'
# print(word3)
# word3 = word3.replace('-', ' ')
# print(word3)
# word3 = word3.replace('‒', ' ')
# print(word3)
# word3 = word3.replace('—', ' ')
# print(word3)

#print('has punctuation:', hasPunctuation, ":", punctuation)


#inv_index = index_articles(file_articles, file_titles)
#test = indexdict_to_string(inv_index)

# print(test)
# print(inv_index)


#exDict = {'exDict': test}

# with open('test.txt', 'w') as file:
#     file.write(json.dumps(exDict))


# tokenizes the whole text article
# def tokenize_article(art_text):
#
#     # transform the text by lowering, removing punctuation and stopwords, and stemming the text
#     art_text = art_text.lower()
#     art_text = art_text.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))
#     token_art_text = art_text.split(' ')
#
#     stop_words = stopwords.words('english')
#     ps = PorterStemmer()
#     token_art_text = [ps.stem(word) for word in token_art_text if word not in stop_words and word != '']
#
#     #return the tokenized article
#     return token_art_text


# -*- coding: utf-8 -*-
# def is_english(s):
#     try:
#         s.encode(encoding='utf-8').decode('ascii')
#     except UnicodeDecodeError:
#         return False
#     else:
#         return True

#from ..common.article.article import Article

# def get_similar(query):
#    a1 = Article(1, query, "This is the first result")
#    a2 = Article(2, "Planet", "This is the second result")
#    a3 = Article(3, "Mars", "This is the thirth result")
#    a4 = Article(4, "Jupiter", "This is the fourth result")
#    return [a1, a2, a3, a4]
