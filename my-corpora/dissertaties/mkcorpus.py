import pandas as pd
import os

#bit = 'sample'
bit = 'full'
info = ['title','topics','abstract']
languages =[]
#languages=['en']#,'en-en', 'en-nl','nl', 'lang']


sd = '/opt2/dissertaties/data_'+ bit
gd = '_'.join([bit]+info+languages)

#sd = '/opt2/dissertaties/data_full'
#gd = 'abstracts'






if not os.path.isdir(gd):
    os.mkdir(gd)
else:
    print('Warning: possibly overwriting content of ' + gd)

ggc = pd.read_excel('ggc_proefschriften_v4.xlsx',dtype=object)

brinkman = pd.read_csv('../brinkmanthesaurus_vocab.tsv', sep='\t', header = None, names = ['uri','label'])

oai = pd.read_csv('meta_oai.csv', sep=';', index_col = 0, dtype=object)
topic_en = [ col for col in oai.columns if 'topic_en' in col]
topic_lang = [ col for col in oai.columns if 'topic_lang' in col]

kinds = ['train','test']
for kind in kinds:
    if not os.path.isdir(os.path.join(gd,kind)): os.makedirs(os.path.join(gd,kind))
    identifiers = pd.read_csv(kind+'_identifiers.csv', sep=';', dtype='object')
    identifiers.dropna(inplace=True) # linked items only


    gold = ggc.merge(identifiers, left_on = 'ppn', right_on='ppn')

    for identifier in identifiers.identifier.unique(): # there are some duplicates in the gold data, ignore them

        # Collect document properties (as harvested from repo)

        print(identifier)

        oai_item = oai.loc[identifier]
        language = oai_item.language
        if languages:
            if language not in languages: continue

        # Collect abstract(s)
        dname = os.path.join(sd,identifier)
        if os.path.isdir(dname):  # The document does not occur in the source dir
            abstracts = {}
            for fname in os.listdir(os.path.join(dname, 'metadata')):
                if 'abstract' not in fname: continue
                try: lang = fname.split('_')[1].split('.')[0]
                except: lang = 'lang'

                try:
                    with open(os.path.join(dname, 'metadata', fname),'r') as f:
                         lines = f.readlines()
                except:
                    with open(os.path.join(dname, 'metadata', fname), 'r', encoding ='iso-8859-1') as f:
                         lines = f.readlines()
                abstracts[lang]=' '.join([line.strip() for line in lines]) # keep empty lines (separators)?
        else:
            print('No abstract??')
            abstracts = pd.Series()

        topics = oai_item[topic_en].dropna()
        if len(topics)==0:
            topics = oai_item[topic_lang].dropna()
        topics = topics.values

        title = oai_item.title
        assert type(title) == str
        if type(oai_item.subTitle) == str: title +=' '+ oai_item.subTitle

        with open(os.path.join(gd,kind,identifier)+'.txt', 'w', encoding='utf-8') as f:
            f.write(title+'\n\n')
            f.write(' '.join(topics)+'\n\n')
            f.write('\n\n'.join(abstracts.values()))

        # Collect labels (as assigned in KB catalogue)
        gold_item = gold.loc[gold.identifier==identifier]
        uris = [gold_item['ppn_brinkman_'+str(d)] for d in range(1,6)]
        uris = [uri for uri in uris if not uri.isna().values[0] ] # drop NaNs
        uris = ['<http://data.bibliotheken.nl/id/thes/p'+uri.values[0]+'>' for uri in uris] # convert to string (proper uri)

        try:
            with open(os.path.join(gd,kind,identifier)+'.tsv', 'w', encoding='utf-8') as f:
                f.write('\n'.join(['\t'.join([uri, brinkman.loc[brinkman.uri==uri,'label'].values[0]]) for uri in uris]))
        except:
            print('\t No labels?? Problem??')



# title
# subtitle
# 
# abstract
# department (?)



