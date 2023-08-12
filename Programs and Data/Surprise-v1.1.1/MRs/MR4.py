# coding=utf-8
# author: Yi Xiaorong
# date: 2020/9/25 16:01
# tool: PyCharm
import os
import random

from surprise import accuracy


def exeMR(raw_trainset, raw_testset, mr_train_test_folder, assertInfo):
    with open(mr_train_test_folder + "raw_trainset.txt", "w") as f:
        for i in range(len(raw_trainset)):
            f.write(str(raw_trainset[i][0]) + "\t" + str(raw_trainset[i][1]) + "\t" + str(raw_trainset[i][2]) + "\n")

    train_columns = 0
    mr_ratings = []
    train_column_ids = []
    test_columns = 0
    mr_test = []
    test_column_ids = []
    chooseRowIndex = -1
    while train_columns == 0 or test_columns == 0:
        train_columns = 0
        test_columns = 0
        train_column_ids.clear()
        test_column_ids.clear()
        chooseRowIndex = raw_trainset[random.randint(0, len(raw_trainset) - 1)][0]
        for i in range(len(raw_trainset)):
            if raw_trainset[i][0] == chooseRowIndex:
                train_columns += 1
                train_column_ids.append(raw_trainset[i][1])

        for i in range(len(raw_testset)):
            if raw_testset[i][0] == chooseRowIndex:
                test_columns += 1
                test_column_ids.append(raw_testset[i][1])

    for item in raw_trainset:
        if item[0] == chooseRowIndex:
            r = item[2] + random.randint(1, 2)
            if r > 5:
                r = 5
            mr_ratings.append((item[0], item[1], r))
        else:
            mr_ratings.append(item)

    for item in raw_testset:
        if item[0] == chooseRowIndex:
            r = item[2] + random.randint(1, 2)
            if r > 5:
                r = 5
            mr_test.append((item[0], item[1], r))
        else:
            mr_test.append(item)

    with open(assertInfo, "w") as f:
        f.write("chooseRowIndex:" + str(chooseRowIndex) + "\n")
        f.write("trainColumns:" + str(train_columns) + "\n")
        f.write("testColumns:" + str(test_columns) + "\n")
        f.write("trainColumnIDs:")
        for id in train_column_ids:
            f.write(str(id) + ",")
        f.write("\n")
        f.write("testColumnIDs:")
        for id in test_column_ids:
            f.write(str(id) + ",")
        f.write("\n")

    with open(mr_train_test_folder + "mr_ratings.txt", "w") as f:
        for i in range(len(mr_ratings)):
            f.write(str(mr_ratings[i][0]) + "\t" + str(mr_ratings[i][1]) + "\t" + str(mr_ratings[i][2]) + "\n")

    with open(mr_train_test_folder + "mr_test.txt", "w") as f:
        for i in range(len(mr_test)):
            f.write(str(mr_test[i][0]) + "\t" + str(mr_test[i][1]) + "\t" + str(mr_test[i][2]) + "\n")


def exeAssert(loop, folder):
    result_mr_data_dict = readResult(folder + "/result_mr.txt")
    result_ori_data_dict = readResult(folder + "/result_ori.txt")

    chooseRowIndex = -1
    testColumns = 0
    testColumnIDs = []
    with open(folder + "assertInfo.txt", "r") as f:
        while True:
            line = f.readline()
            line = line.strip('\n')
            line = line.strip(',')
            if not line:
                break
            if "chooseRowIndex:" in line:
                chooseRowIndex = line.split(":")[1]
            if "testColumns:" in line:
                testColumns = int(line.split(":")[1])
            if "testColumnIDs:" in line:
                for id in line.split(":")[1].split(","):
                    testColumnIDs.append(id)

    count = 0
    with open(folder + "assertInfo.txt", "a") as f:
        f.write("将选中行的所有训练集评分数据 + △，△的取值范围是[1,2]，该行的预测值应升高\n\n")
        f.write("userID\titemID\tresult_ori\t\t\tresult_mr\t\t\tresult_difference\n")
        for colId in testColumnIDs:
            if float(result_mr_data_dict[chooseRowIndex][colId]) - float(result_ori_data_dict[chooseRowIndex][colId]) < 0:
                count += 1
                f.write(chooseRowIndex + "\t" +
                        colId + "\t" +
                        result_ori_data_dict[chooseRowIndex][colId] + "\t\t" +
                        result_mr_data_dict[chooseRowIndex][colId] + "\t\t" +
                        str(float(result_mr_data_dict[chooseRowIndex][colId]) - float(result_ori_data_dict[chooseRowIndex][colId])) + "\n")

        if count == 0:
            f.write("\nAssert: TRUE\nPercent: 0.0")
        else:
            f.write("\nAssert: FALSE\nPercent: " + str(count / testColumns))

    if loop == 100:
        statisticalResult(loop, folder)


def savePredictionsAndAccuracy(result, resultEvo, predictions):
    with open(result, "w") as f:
        for prediction in predictions:
            row = str(prediction[0]) + "\t" + str(prediction[1]) + "\t" + str(prediction[3]) + "\n"
            f.write(row)

    with open(resultEvo, "w") as f:
        f.write("RMSE:" + str(accuracy.rmse(predictions, False)) + "\n")
        f.write("RAE:" + str(accuracy.mae(predictions, False)) + "\n")


def saveUserAndItemMapping(userMapping, itemMapping, train_set):
    with open(userMapping, "w") as f:
        for iuid in train_set.all_users():
            row = str(train_set.to_raw_uid(iuid)) + "b" + str(iuid) + "\n"
            f.write(row)

    with open(itemMapping, "w") as f:
        for iiid in train_set.all_items():
            row = str(train_set.to_raw_iid(iiid)) + "b" + str(iiid) + "\n"
            f.write(row)


def readResult(file):
    dict = {}
    with open(file, "r") as f:
        while True:
            line = f.readline()
            line = line.strip('\n')
            if not line:
                break

            raw = line.split(sep='\t')

            if raw[0] not in dict:
                colAndVal = {raw[1]: raw[2]}
                dict[raw[0]] = colAndVal
            else:
                dict[raw[0]][raw[1]] = raw[2]

    return dict


def statisticalResult(loop, folder):
    pass_count = 0
    failure = 0
    average_percent = 0
    infoFile = folder.split("loop")[0] + "info.txt"
    for i in range(1, loop + 1):
        assertFile = folder.split("loop")[0] + "loop" + str(i) + "/assertInfo.txt"
        with open(assertFile, "r") as assertFilef:
            while True:
                line = assertFilef.readline()
                if not line:
                    break

                if "Assert:" in line:
                    line = line.strip('\n')
                    if line.split(": ")[1] == "TRUE":
                        pass_count = pass_count + 1
                        break
                    else:
                        failure = failure + 1

                if "Percent:" in line:
                    average_percent = average_percent + float(line.split("Percent: ")[1])

        with open(infoFile, "a") as infoFilef:
            usermap = readMapping(folder.split("loop")[0] + "loop" + str(i) + "/train_test/userMapping.txt")
            itemmap = readMapping(folder.split("loop")[0] + "loop" + str(i) + "/train_test/itemMapping.txt")
            mr_usermap = readMapping(folder.split("loop")[0] + "loop" + str(i) + "/mr_train_test/userMapping.txt")
            mr_itemmap = readMapping(folder.split("loop")[0] + "loop" + str(i) + "/mr_train_test/itemMapping.txt")
            infoFilef.write("loop" + str(i) + ": userMappingNum=" + str(len(usermap.difference(mr_usermap))) +
                            ", itemMappingNum=" + str(len(itemmap.difference(mr_itemmap))) + "\n")

    with open(infoFile, "a") as infoFilef:
        if failure == 0:
            infoFilef.write(str(pass_count) + "," + str(failure) + "," + "0\n")
        else:
            infoFilef.write(str(pass_count) + "," + str(failure) + "," + str(average_percent / failure) + "\n")
    print("----------")
    print("Successed!")
    print("----------")


def readMapping(file):
    list = []
    with open(file, "r") as f:
        while True:
            line = f.readline()
            line = line.strip('\n')
            if not line:
                break

            list.append(line)

    return set(list)


class MR4:
    def __init__(self, raw_trainset, raw_testset, train_set, test_set, predictions, loop, folder, split_model):
        self.raw_trainset = raw_trainset
        self.raw_testset = raw_testset
        self.train_set = train_set
        self.test_set = test_set
        self.predictions = predictions
        self.loop = loop
        self.split_model = split_model

        self.train_test_folder = folder + "train_test/"
        self.mr_train_test_folder = folder + "mr_train_test/"

        self.assertInfo = folder + "assertInfo.txt"
        if split_model == "SIMPLE_SPLIT":
            os.makedirs(folder)
            os.makedirs(self.train_test_folder)
            os.makedirs(self.mr_train_test_folder)

            self.userMapping = self.train_test_folder + "userMapping.txt"
            self.itemMapping = self.train_test_folder + "itemMapping.txt"
            self.result = folder + "result_ori.txt"
            self.resultEvo = folder + "result_evo_ori.txt"

            savePredictionsAndAccuracy(self.result, self.resultEvo, self.predictions)
            saveUserAndItemMapping(self.userMapping, self.itemMapping, self.train_set)
            # 通过MR计算并保存训练集与测试集
            exeMR(raw_trainset, raw_testset, self.mr_train_test_folder, self.assertInfo)

        if split_model == "PREDEFINED_SPLIT":
            self.userMapping = self.mr_train_test_folder + "userMapping.txt"
            self.itemMapping = self.mr_train_test_folder + "itemMapping.txt"
            self.result = folder + "result_mr.txt"
            self.resultEvo = folder + "result_evo_mr.txt"

            savePredictionsAndAccuracy(self.result, self.resultEvo, self.predictions)
            saveUserAndItemMapping(self.userMapping, self.itemMapping, self.train_set)

            exeAssert(loop, folder)
