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
    #return InL2Ranker(some_param=1.0) 
    #return metapy.index.JelinekMercer(0.6100000000000003)
    #return metapy.index.DirichletPrior(209)
    #return metapy.index.OkapiBM25(k1=1.48, b=0.744, k3 = .75)
    return metapy.index.OkapiBM25(k1=1.485, b=0.75, k3 = 0.7)
    

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: {} config.toml".format(sys.argv[0]))
        sys.exit(1)

    cfg = sys.argv[1]
    print('Building or loading index...')
    param1 = 1

    
    p1 = 0
    p2 = 0
    p3 = 0
    p11 = 0
    p22 = 0
    p33 = 0
    b = 0
    idx = metapy.index.make_inverted_index(cfg)
    while param1 < 2 :
        print(param1) 
        param2 = 0.50
        while param2 < 1 :            
            print(' ' ,param2)
            param3 = 0.50
            while param3 < 1:
                param3= param3+ 0.05
                ranker = metapy.index.OkapiBM25(k1=param1, b=param2, k3 = param3)
                #ranker = load_ranker(cfg)
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

                if b < ndcg :
                    b = ndcg
                    p1 = param1
                    p2 = param2
                    p3 = param3
                    print('  change ',p1 , ' ' , p2 , ' ' , p3, ' ', b)  
                if ndcg == 0.3657152373135 :
                    print(param1 , ' ' , param2 , ' ' , param3)   
                    p11 = param1
                    p22 = param2
                    p33 = param3             
            pass
            param2 = param2 + 0.01
        pass
        param1 = param1 + 0.01  
        
    pass
print('rank 1', p11 , ' ',p22 , ' ' ,p33)
print('best ', p1 , ' ',p2 , ' ' ,p3)

