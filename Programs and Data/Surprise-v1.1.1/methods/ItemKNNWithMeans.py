# coding=utf-8
# author: Yi Xiaorong
# date: 2020/9/25 11:11
# tool: PyCharm

from surprise import Reader, KNNWithMeans
from surprise import Dataset
from surprise.model_selection import train_test_split, PredefinedKFold

from MRs.MR1 import MR1
from MRs.MR2 import MR2
from MRs.MR3 import MR3
from MRs.MR4 import MR4
from MRs.MR5 import MR5
from MRs.MR6 import MR6

def getMR(MR, raw_trainset, raw_testset, trainset, testset, predictions, loop, folder, split_model):
    mr = None
    if MR == "MR1":
        mr = MR1(raw_trainset, raw_testset, trainset, testset, predictions, loop, folder, split_model)
    elif MR == "MR2":
        mr = MR2(raw_trainset, raw_testset, trainset, testset, predictions, loop, folder, split_model)
    elif MR == "MR3":
        mr = MR3(raw_trainset, raw_testset, trainset, testset, predictions, loop, folder, split_model)
    elif MR == "MR4":
        mr = MR4(raw_trainset, raw_testset, trainset, testset, predictions, loop, folder, split_model)
    elif MR == "MR5":
        mr = MR5(raw_trainset, raw_testset, trainset, testset, predictions, loop, folder, split_model)
    elif MR == "MR6":
        mr = MR6(raw_trainset, raw_testset, trainset, testset, predictions, loop, folder, split_model)

    return mr


def exe(algo, split_model, MR, reader):
    for i in range(100):
        trainset = None
        testset = None
        raw_trainset = None
        raw_testset = None

        folder = "E:/MT/surprise_data/" + algo.name + "/" + MR + "/loop" + str(i + 1) + "/"
        if split_model == "SIMPLE_SPLIT":
            data = Dataset.load_builtin("ml-100k")
            raw_trainset, raw_testset, trainset, testset = train_test_split(data, test_size=0.2)
        if split_model == "PREDEFINED_SPLIT":
            folds_files = [(folder + 'mr_train_test/mr_ratings.txt', folder + 'mr_train_test/mr_test.txt')]
            data = Dataset.load_from_folds(folds_files, reader=reader)
            pkf = PredefinedKFold()
            trainset, testset = next(pkf.split(data))

        algo.fit(trainset)
        predictions = algo.test(testset)

        mr = getMR(MR, raw_trainset, raw_testset, trainset, testset, predictions, i + 1, folder, split_model)


if __name__ == "__main__":
    setattr(KNNWithMeans, "name", "ItemKNNWithMeans")
    algo = KNNWithMeans(sim_options={'user_based':False})

    # split_model = "SIMPLE_SPLIT"
    split_model = "PREDEFINED_SPLIT"

    exe(algo, split_model, "MR1", reader=Reader(sep='\t'))
    exe(algo, split_model, "MR2", reader=Reader(sep='\t', rating_scale=(1, 50)))  # 取值范围为 [1, 10] 数乘
    exe(algo, split_model, "MR3", reader=Reader(sep='\t', rating_scale=(2, 10)))  # 取值范围为 [1, 5] 数加
    exe(algo, split_model, "MR4", reader=Reader(sep='\t'))
    exe(algo, split_model, "MR5", reader=Reader(sep='\t'))
    exe(algo, split_model, "MR6", reader=Reader(sep='\t'))
