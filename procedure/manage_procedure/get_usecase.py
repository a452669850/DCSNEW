# -*- coding: UTF-8 -*-

from models import Usecase
import json
def print_prase_result(usecase_number):
    usecase = Usecase.get(Usecase.number ==usecase_number)
    oper = json.loads(usecase.operation)
    print "这是用例:",usecase.name,"\n" ,usecase.number,"\n",usecase.IC
    for item in oper:
        print item[0]
        for i in range(1,len(item)):
            if len(item[i]) <2:
                print item[i][0]
            if item[i][0] != "READ":
                print item[i][0],item[i][1]["name"],item[i][1]["formula"]
            if item[i][0] == "READ":
                print "READ"
                for j in range(1,len(item[i])):
                    print item[i][j]["name"],item[i][j]["formula"],item[i][j]["delay_time"]

if __name__ == "__main__":
    print_prase_result("TP3RPN01M002")