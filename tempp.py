def search_for_paragraphs(search_term, num_results, index) -> str:
    block = search_term.split("，").split("的").reverse()
    temp_index = index
    temp_datas = datas
    max_num = 200
    for b in block:
        temp_index, temp_datas = search_for_block(b, max_num, temp_index, temp_datas)
        max_num = max(max_num - 10, 10)
    search_vector = convert_text_to_vector(search_term)
    search_vector = np.array([search_vector]).astype('float32')
    distances, indexes = temp_index.search(search_vector, num_results)
    anss = ''
    for i, (distance, index) in enumerate(zip(distances[0], indexes[0])):
        path = temp_datas['file_path'][index]
        num = temp_datas['text_num'][index]
        with open(path, 'r') as file:
            data = json.load(file)
            anss = anss + '\n' + data[num]
    return anss

def search_for_block(b, search_num ,index, tdatas):
    search_vector = convert_text_to_vector(b)
    search_vector = np.array([search_vector]).astype('float32')
    distances, indexes = index.search(search_vector, search_num)
    temp_vectors = []
    temp_datas = []
    for i, (distance, index) in enumerate(zip(distances[0], indexes[0])):
        vector = tdatas['vectors'][index]
        temp_vectors.append(np.array(vector))
        temp_datas.append(tdatas[index])
    block_vectors = np.stack(temp_vectors).astype('float32')
    temp_dimension = block_vectors.shape[1]
    temp_index = faiss.IndexFlatL2(temp_dimension)
    temp_index.add(block_vectors)
    return temp_index, temp_datas
