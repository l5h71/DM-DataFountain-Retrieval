import json
import os
#from pypdf import PdfReader
import pdfplumber
import re

class PDF:

    pdf_path = ''
    data = []

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def SlidingWindow(self, sentences, kernel = 512, stride = 1):
        sz = len(sentences)
        cur = ""
        fast = 0
        slow = 0
        sentence = ""
        while (fast < len(sentences)):
            sentence = sentences[fast]
            if (len(cur + sentence) > kernel and (cur + sentence) not in self.data):
                sent = cur + sentence + '。'
                sent = sent.encode('utf-8', 'ignore').decode('utf-8')
                # sent = re.sub(r'[^\w\s\u4e00-\u9fa5，。“”：；《》？……（）]', '', sent)
                # sent = re.sub(r'\.{1,5}', '', sent)
                # sent = re.sub(r'\.{7,}', '', sent)
                if 'CCFBDCI' in sent or '仅允许在本次比赛中使用' in sent:
                    print('continue')
                else:
                    self.data.append(sent)
                cur = cur[len(sentences[slow] + "。"):]
                slow = slow + 1
            cur = cur + sentence + "。"
            fast = fast + 1

    def ParseAllPage(self, max_seq=256, min_len=4):
        all_content = ""
        all_table_content = ""
        sentences = []
        sentence = ""
        pdf = pdfplumber.open(self.pdf_path)
        for idx, page in enumerate(pdf.pages):

            pre_left_position = 0
            pre_right_position = 0
            words = page.extract_words()
            # 打印每个单词及其位置
            for word in words:
                left_position = word['x0']
                right_position = word['x1']
                #print(word['text'], word['x0'], word['x1'], word['top'], word['bottom'])
                if (abs(left_position - pre_left_position) > 0.5) & (abs(right_position - pre_right_position) > 0.5):
                    sentences.append(sentence)
                    pre_left_position = left_position
                    pre_right_position = right_position
                    sentence = ""
                text = word['text'].strip().strip("\n")
                if ("...................." in text or "目录" in text):
                    continue
                if (len(text) < 1):
                    continue
                # if (text.isdigit()):
                #     continue
                sentence = sentence + text

            table_content = ""
            tables = page.extract_tables()
            #将表格按行存储
            for table_index, table in enumerate(tables):
                table_content = table_content + " ___Table Index: " + (table_index + 1).__str__() + "___"
                for row_index, row in enumerate(table):
                    table_content = table_content + "---Row Index: " + (row_index + 1).__str__() + "---"
                    for item in row:
                        if item != None:
                            table_content = table_content + " " + item.__str__().strip("\n").strip()
            all_table_content = all_table_content + table_content
        sentences.append(sentence)
        sentences = sentences + all_table_content.split("。")
        para_content = ""
        for s in sentences:
            sentence_content = ""
            words = s.split("\n")
            for idx, word in enumerate(words):
                text = word.strip().strip("\n")
                if("...................." in text or "目录" in text):
                    continue
                if(len(text) < 1):
                    continue
                sentence_content = sentence_content + text
            if len(sentence_content) < min_len:
                continue
            para_content = para_content + sentence_content
        para = para_content.split("。")
        self.SlidingWindow(para, kernel=max_seq)


# 批量处理 PDF 文件
# pdf_folder = 'D:\\桌面\\DM-DataFountain-Retrieval\\resources\\A_document'
pdf_folder = '/home/lsh/DM-DataFountain-Retrieval/resources/A_document'
# output_folder = 'D:\\桌面\\DM-DataFountain-Retrieval\\resources\\temp'
output_folder = '/home/lsh/DM-DataFountain-Retrieval/resources/temp'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

i = 1
for pdf_file in os.listdir(pdf_folder):
    if pdf_file.endswith('.pdf'):
        pdf = PDF(pdf_folder + '/' + pdf_file)
        pdf.ParseAllPage()
        with open(output_folder + '/' + str(i) + '.json', 'w', encoding='utf-8') as file:
            json.dump(pdf.data, file, ensure_ascii=False, indent=4)
        print('finish' + str(i))
        i = i + 1


print("所有PDF文件已解析并保存为文本文件。")

