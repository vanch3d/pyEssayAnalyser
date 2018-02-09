from collections import namedtuple

from EssayAnalyser.ea_results_v3 import make_results_array
from EssayAnalyser.ke_all_v3 import process_essay_ke, get_essay_stats_ke
from EssayAnalyser.se_graph_v3 import sample_nodes_for_figure
from EssayAnalyser.se_print_v3 import get_essay_stats_se
from EssayAnalyser.se_procedure_v3 import pre_process_text, process_essay_se

Data = namedtuple("Data", [
    "text_se",
    "parasenttok",
    "wordtok",
    "b_last",
    "len_refs",
    "refsheaded",
    "late_wc",
    "appendixheaded",
    "section_names",
    "section_labels",
    "headings",
    "conclheaded",
    "c_first",
    "c_last",
    "introheaded",
    "i_first",
    "i_last",
    "number_of_words"])

SGraph = namedtuple("SGraph", "gr_se ranked_global_weights reorganised_array")
KGraph = namedtuple("KGraph", "text_ke gr_ke di myarray_ke keylemmas keywords "
                              "bigram_keyphrases trigram_keyphrases quadgram_keyphrases threshold_ke")

SeStats = namedtuple("SeStats", "paras rankorder countProseSents countProseChars len_headings "
                                "countSentLen truesents countTrueSent countTrueSentChars countFalseSent "
                                "countAvSentLen countIntroSent countIntroChars countConclSent "
                                "countConclChars countAssQSent  countTableEnt countListItem "
                                "countTitleSent percent_body_i i_toprank percent_body_c "
                                "c_toprank nodes edges edges_over_sents")

KeStats = namedtuple("KeStats", "scoresNfreqs fivemostfreq avfreqsum uls_in_ass_q_long kls_in_ass_q_long "
                                "sum_freq_kls_in_ass_q_long kls_in_ass_q_short sum_freq_kls_in_ass_q_short "
                                "kls_in_tb_index sum_freq_kls_in_tb_index bigrams_in_intro1 bigrams_in_intro2 "
                                "bigrams_in_concl1 bigrams_in_concl2 bigrams_in_assq1 bigrams_in_assq2 all_bigrams "
                                "topbetscore")

Sample = namedtuple("Sample","gr_se_sample gr_ke_sample")

class Essay:
    """
    Wrapper for the essay analyser
    @todo[vanch3d]  refine output; trim unnecessary and duplicated data; split data and metadata
    @todo[vanch3d]  add profiler for deeper optimisation
    """

    def __init__(self, txt: str):
        """
        Default constructor
        :param txt: The text (plain text, utf-8) to be processed
        """

        self.text = txt
        self.data = {}
        self.meta = {}

    def process(self):
        """
        Launch the processing of the text
            - pre-processing
            - key sentence extraction
            - key words extraction
            - key sentence & key word analytics
            - sentence & word graph generation
            - package data & metadata
        :return: the Essay object itself
        """
        data = self.__pre_process_text()
        se = self.__process_essay_se(data)
        ke = self.__process_essay_ke(data)
        sstats = self.__get_essay_stats_se(data, se)
        kstats = self.__get_essay_stats_ke(data,ke)
        sample = self.__get_essay_graphs(se,sstats,ke)

        print("############# PACKAGE DATA & METADATA")
        self.data = self.__make_results_array(data,ke,se,sstats,kstats,sample)

        print("############# FiNISH")
        return self

    def __pre_process_text(self):
        print("############# PRE-PROCESSING")
        return Data._make(pre_process_text(self.text, None, None, None, "NVL"))

    def __process_essay_se(self, d: Data):
        print("############# KEY SENTENCES")
        return SGraph._make(process_essay_se(d.text_se, d.parasenttok, d.section_labels, None, None, "NVL"))

    def __process_essay_ke(self, d: Data):
        print("############# KEY WORDS")
        return KGraph._make(process_essay_ke(d.text_se, d.wordtok, None, None, "NVL"))

    def __get_essay_stats_se(self, d: Data, s: SGraph):
        print("############# STATS KEY SENTENCES")
        return SeStats._make(get_essay_stats_se(s.gr_se, d.text_se, d.headings, s.ranked_global_weights,
                                                s.reorganised_array))

    def __get_essay_stats_ke(self, d: Data, k: KGraph):
        print("############# STATS KEYWORDS")
        return KeStats._make(get_essay_stats_ke(d.text_se, k.gr_ke, k.di, k.myarray_ke, k.keylemmas, k.keywords,
                                                k.bigram_keyphrases, k.trigram_keyphrases, k.quadgram_keyphrases,
                                                [], [], [], [], [], []))

    def __get_essay_graphs(self, s: SGraph, se: SeStats,k: KGraph):
        print("############# GENERATE KE/SE GRAPHS")
        gr_se_sample = sample_nodes_for_figure(s.gr_se, se.truesents, 'se')
        gr_ke_sample = sample_nodes_for_figure(k.gr_ke, k.keylemmas, 'ke')
        return Sample(gr_se_sample,gr_ke_sample)

    def __make_results_array(self, d: Data, k: KGraph, s: SGraph, se: SeStats, ke: KeStats, sp: Sample):
        print("############# PACKAGE RESULTS")
        return make_results_array(d.parasenttok, k.myarray_ke, sp.gr_ke_sample,
                                   se.paras, d.number_of_words,
                                   se.countTrueSent, se.countAvSentLen,
                                   se.nodes, se.edges, sp.gr_se_sample, se.edges_over_sents,
                                   s.ranked_global_weights, s.reorganised_array, k.threshold_ke,
                                   se.len_headings,
                                   se.countAssQSent, se.countTitleSent,
                                   d.b_last, se.countProseSents, d.len_refs, d.refsheaded, d.late_wc, d.appendixheaded,
                                   d.introheaded, d.i_first, d.i_last, se.i_toprank, se.countIntroSent, se.percent_body_i,
                                   d.conclheaded, d.c_first, d.c_last, se.c_toprank, se.countConclSent, se.percent_body_c,
                                   k.keylemmas, k.keywords, ke.fivemostfreq, k.bigram_keyphrases, k.trigram_keyphrases,
                                   k.quadgram_keyphrases,
                                   ke.scoresNfreqs, ke.avfreqsum,
                                   ke.kls_in_ass_q_long, ke.sum_freq_kls_in_ass_q_long,
                                   ke.kls_in_ass_q_short, ke.sum_freq_kls_in_ass_q_short,
                                   ke.kls_in_tb_index, ke.sum_freq_kls_in_tb_index,
                                   ke.all_bigrams)
