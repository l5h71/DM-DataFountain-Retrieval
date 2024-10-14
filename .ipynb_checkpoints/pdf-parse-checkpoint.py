import json
import os
from pypdf import PdfReader
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
        while(fast < len(sentences)):
            sentence = sentences[fast]
            if(len(cur + sentence) > kernel and (cur + sentence) not in self.data):
                sent = cur + sentence + '。'
                sent = sent.encode('utf-8', 'ignore').decode('utf-8')
                sent = re.sub(r'[^\w\s\u4e00-\u9fa5，。“”：；《》？……（）]', '', sent)
                sent = re.sub(r'\.{1,5}', '', sent)
                sent = re.sub(r'\.{7,}', '', sent)
                if 'CCFBDCI' in sent or '仅允许在本次比赛中使用' in sent:
                    print('continue')
                else:
                    self.data.append(sent)
                cur = cur[len(sentences[slow] + "。"):]
                slow = slow + 1
            cur = cur + sentence + "。"
            fast = fast + 1
            
    def ParseAllPage(self, max_seq = 512, min_len = 6):
        all_content = ""
        for idx, page in enumerate(PdfReader(self.pdf_path).pages):
            page_content = ""
            text = page.extract_text()
            words = text.split("\n")
            for idx, word in enumerate(words):
                text = word.strip().strip("\n")
                if("...................." in text or "目录" in text):
                    continue
                if(len(text) < 1):
                    continue
                if(text.isdigit()):
                    continue
                page_content = page_content + text
            if(len(page_content) < min_len):
                continue
            all_content = all_content + page_content
        sentences = all_content.split("。")
        self.SlidingWindow(sentences, kernel = max_seq)


# 批量处理 PDF 文件
pdf_folder = '/home/liusihan/dev/DM-DataFountain-Retrieval/resources/A_document'
output_folder = '/home/liusihan/dev/DM-DataFountain-Retrieval/resources/temp'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

i = 1
for pdf_file in os.listdir(pdf_folder):
    if pdf_file.endswith('.pdf'):
        pdf = PDF(pdf_folder + '/' + pdf_file)
        pdf.ParseAllPage()
        with open(output_folder + '/' + str(i) + '.json', 'w') as file:
            json.dump(pdf.data, file, ensure_ascii=False, indent=4)
        print('finish' + str(i))
        i = i + 1


print("所有PDF文件已解析并保存为文本文件。")
