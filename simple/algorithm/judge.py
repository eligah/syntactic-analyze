from simple.algorithm.syntacticAnalysis import SyntacticAnalysis


def test(washed_list, segs_list, ltp_list, id_list):
    judge = SyntacticAnalysis(host='localhost')
    judge.train()
    return judge.test(washed_list, segs_list, ltp_list, id_list)
