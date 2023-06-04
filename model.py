import uuid
import json


class Subject:
    
    def __init__(self, name, exams):
        self.id = str(uuid.uuid4())
        self.name = name
        self.exams = exams 
    
    def __eq__(self, other):
      if isinstance(other, Subject):
         return self.id == other.id
      return False

class Exam:
    
    def __init__(self, year, questions):
        self.id = str(uuid.uuid4())
        self.year = year
        self.questions = questions

    def __eq__(self, other):
      if isinstance(other, Exam):
         return self.id == other.id
      return False

class Question:
    
    ABCD = ['A', 'B', 'C', 'D']
        
    def __init__(self, num, year, content, options, ans = -1):
        self.id = str(uuid.uuid4())
        self.num = num
        self.year = year
        self.content = content
        self.options = options
        self.ans = ans

    def __eq__(self, other):
      if isinstance(other, Question):
         return self.id == other.id
      return False
    
    def __str__(self):
        txt = f"{self.year} 年度 第 {self.num} 題\n"         # 年度 題號
        txt += f"{self.content}\n"                          # 題目
        for i in range(len(self.options)):                  # 選項
            txt += f"{self.ABCD[i]}. {self.options[i]}\n"    
        # txt += f'Ans: {self.ans}'                         #答案
        return txt

    def is_correct(self, reply: str)-> bool:
        if isinstance(reply, int):
            return self.ans == reply
        elif isinstance(reply, str):
            s = reply.strip().upper()
            if  s in self.ABCD:
                return self.ans == self.ABCD.index(s)
            else:
                return False
        else:
            return False

    def ans_byStr(self, string: str):
        # if rate not in self.ABCD:
        #     raise ValueError("Invalid ansner. Please enter A, B, C, D ")
        s = string.strip().upper()
        if s in self.ABCD:
            self.ans = self.ABCD.index(s)
        else:
            self.ans = -1

    def get_ans(self):
        if self.ans in [0, 1, 2, 3]:
            return self.ABCD[self.ans]
        else:
            return 'no answer.'

# the class used when dumps object 
class SubjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Subject):
            return obj.__dict__
        elif isinstance(obj, Exam):
            return obj.__dict__
        elif isinstance(obj, Question):
            return obj.__dict__
        return super().default(obj)


# return str in json
def subject_to_json(subject: Subject):
    return json.dumps(subject, cls=SubjectEncoder)

# Subject list to JSON
def subject_list_to_json(subject_list):
    subjects = []
    for subject in subject_list:
        subjects.append(subject.__dict__)
    return json.dumps(subjects, cls=SubjectEncoder)


# the object_hook used when load json
def from_json(json_obj):
    if 'name' in json_obj and 'exams' in json_obj:
        subject = Subject(json_obj['name'], {})
        for year, exam_data in json_obj['exams'].items():
            exam = Exam(year, {})
            for num, question_data in exam_data['questions'].items():
                question = Question(
                    num=question_data['num'],
                    year=question_data['year'],
                    content=question_data['content'],
                    options=question_data['options'],
                    ans=question_data['ans']
                )
                exam.questions[int(num)] = question
            subject.exams[int(year)] = exam
        return subject
    return json_obj


def json_to_subject(json_str: str):
    return json.loads(json_str, object_hook=from_json)

# JSON to Subject list
def json_to_subject_list(json_obj_list):
    obj_list = json.loads(json_obj_list)
    subject_list = []
    for obj in obj_list:
        subject = from_json(obj)
        subject_list.append(subject)
    return subject_list


if __name__ == "__main__":

    q = Question(
        num = 1,
        year = 104,
        content ='依涉外民事法律適用法第48 條，夫妻財產制，夫妻以書面合意適用其一方之本國法或住所地法者，依其合意所定之法律。夫妻無前項之合意或其合意依前項之法律無效時，其夫妻財產制首先依照：',
        options = ['依共同之住所地法', '依夫妻共同之本國法', '依各該當事人之本國法', '依與夫妻婚姻關係最切地之法律'],
    )
    q.ans_byStr('A')
    print(q)

    s = Subject(
        name = "移民法",
        exams = {
            104: Exam(
                year= 104,
                questions= {q.num: q}
            )
        }
    )

    # subject_to_json example
    s_json = subject_to_json(s)
    print(f'Type of json: {type(s_json)}')
    
    # json_to_subject example
    print(f'____________object from json_______________')
    subject_obj = json_to_subject(s_json)
    print(subject_obj.exams[104].questions[1])

    # subject_list_to_json example
    s_list_json = subject_list_to_json([s])
    print(f'Type of json: {type(s_list_json)}')
    
    # json_to_subject_list example
    print(f'____________object list from json_______________')
    subject_obj_list = json_to_subject_list(s_list_json)
    print(f'{len(subject_obj_list)} subject in list.')
    print(subject_obj_list[0].exams[104].questions[1])