import math
import sys
import time
import metapy
import pytoml


class InL2Ranker(metapy.index.RankingFunction):
    """
    Create a new ranking function in Python that can be used in MeTA.
    """
    def __init__(self, some_param=1.0):
        self.param = some_param
        # You *must* call the base class constructor here!
        super(InL2Ranker, self).__init__()

    def score_one(self, sd):
        """
        You need to override this function to return a score for a single term.
        For fields available in the score_data sd object,
        @see https://meta-toolkit.org/doxygen/structmeta_1_1index_1_1score__data.html
        """
        
        #print('here',sd.doc_term_count)
        #sd.d_id * math.log(1 + avg_dl ,2) 
        #tfn = c(t,d) * ln(1 + avdl/|d|)

        lda = sd.num_docs / sd.corpus_term_count
        tfn = sd.doc_term_count * math.log(1.0 +  sd.avg_dl /
                sd.doc_size,2)

        numerator = tfn * math.log((sd.num_docs+1)/(sd.corpus_term_count + 0.5),2)
        return sd.query_term_weight * numerator / (tfn + self.param)
        


def load_ranker(cfg_file):
    """
    Use this function to return the Ranker object to evaluate, e.g. return InL2Ranker(some_param=1.0) 
    The parameter to this function, cfg_file, is the path to a
    configuration file used to load the index. You can ignore this for MP2.
    """
    #return metapy.index.OkapiBM25(k1=1.485, b=0.75, k3 = 0.7)
    #return metapy.index.OkapiBM25(k1=1.82, b=0.6999, k3 = 1.162)
    #logging.warning('here')
    #return metapy.index.OkapiBM25(k1=1.2, b=0.75, k3 = 0.3)



  
    return metapy.index.OkapiBM25(k1=3.6, b=0.699, k3 = 0.5)
    
def callmethod(p1,p2,p3):
    if len(sys.argv) != 2:
        print("Usage: {} config.toml".format(sys.argv[0]))
        sys.exit(1)

    cfg = sys.argv[1]
    idx = metapy.index.make_inverted_index(cfg)
    ranker = metapy.index.OkapiBM25(k1=p1, b=p2, k3 = p3)
    ev = metapy.index.IREval(cfg)

    with open(cfg, 'r') as fin:
        cfg_d = pytoml.load(fin)

    query_cfg = cfg_d['query-runner']
    if query_cfg is None:
        print("query-runner table needed in {}".format(cfg))
        sys.exit(1)

    start_time = time.time()
    top_k = 10
    query_path = query_cfg.get('query-path', 'queries.txt')
    query_start = query_cfg.get('query-id-start', 0)

    query = metapy.index.Document()
    ndcg = 0.0
    num_queries = 0


    with open(query_path) as query_file:
        for query_num, line in enumerate(query_file):
            query.content(line.strip())
            results = ranker.score(idx, query, top_k)
            ndcg += ev.ndcg(results, query_start + query_num, top_k)
            num_queries+=1
    ndcg= ndcg / num_queries
            
    return ndcg

if __name__ == '__main__':
    
    p1= 0
    p2=0
    p3 = 0
    i = 13
    param = 0
    while  i < 16 :
        j = .1
        while j < 10 :
            k = .1
            while k < 1000 :
                tempparam = callmethod(i, j, k)
                #print(tempparam)
                if param < tempparam :
                    param = tempparam
                    p1 =i
                    p2 =j
                    p3 = k
                k = k + 0.1                
            j = j + 0.1
            print( "best ",p1 , " " , p2 , " ", p3 , " ", param )
        i = i + 1
