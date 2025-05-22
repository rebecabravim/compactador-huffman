# huffman.py
import os
from tkinter import filedialog, messagebox, Tk, Button, Label
from graphviz import Digraph
import os

class Node:

    """
    Representa um nó da árvore de Huffman

    Atributos:
    char: o caráter do texto (pode ser nulo).
    freq: a frequência do caráter no texto (ou a soma dos nós filhos).
    left: nó filho à esquerda.
    right: nó filho a direita

    """

    def __init__(self, char=None, freq=0):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        # Essa função permite comparar dois nós pela frequência usando o símbolo menor que
        return self.freq < other.freq


def dic_freq(text):
    '''
    A partir do texto fornecido cria uma estrutura de dados com a frequência de 
    cada caráter no texto
    
    Parâmetros:
    text: texto para contruir a tabela

    Retorna:
    Dicionário cuja chave é o caráter e valor sua frequência
    '''
    freq = {}
    for char in text:
        freq[char] = freq.get(char, 0) + 1
    return dict(sorted(freq.items(), key=lambda item: item[1]))


def arvore_huffman(freq_table):
    '''
    A partir do dicionário fornecido cria a árvore de Huffman.
    
    Parâmetros:
    freq_table: dicionário contendo a frequência de cada caráter.

    Retorna:
    O nó raiz da árvore de Huffman.

    '''
    # Priemeiramente, cria-se os nós e os coloca em uma fila
    fila = [Node(char, freq) for char, freq in freq_table.items()]


    while len(fila) > 1:

        # Ordena (ou reeordena) os nós em ordem crescente.
        fila.sort(key=lambda node: node.freq)
        # Tira o menor nó da fila e armazena na variável node1.
        node1 = fila.pop(0)
        # Tira o segundo menor nó da fila (que agora é o menor pois
        # já tiramos o menor) e armazena na variável node2.
        node2 = fila.pop(0)
        # Cria um nó sem caráter com a soma dos nós menores.
        merge = Node(None, node1.freq + node2.freq)
        # O nó a esquerda desse novo nó é o menor (node1, visto que
        # a lista está ordenada) e o nó da direita o maior (node2).
        merge.left = node1
        merge.right = node2
        # Adiciona o novo nó à fila e repete o laço até que reste
        # apenas 1 elemento na fila.
        fila.append(merge)

    # Quando a fila só tem 1 elemento, todas as combinações foram
    # feitas, e esse nó que sobrou é a raiz da árvore de huffman.
    return fila[0]


def criar_codigos(node, current_code="", codes={}):
    '''
    Função recursiva que percorre a árvore. Recebe o nó raiz da árvore e retorna 
    um dicionário com o valor codificado de cada caráter presente na árvore.

    Parâmetros:
    node: nó raiz da árvore
    current_code: o código sendo montado de um determinado caráter.
    codes: o dicionário contendo os valores em binário de cada caráter.

    Retorna:
    O dicionário contendo os valores em binário de cada caráter.
    '''

    # Quando caminha e não um nó, não faz nada
    if node is None:
        return
    # Quando acha um nó com algum caráter adiciona na lista dos códigos
    # o código do caráter
    if node.char is not None:
        codes[node.char] = current_code

    # Enquanto não acha o nó caminha para a esquerda e para
    # direita, quando caminha para a esquerda adiciona 0 ao código
    # do caráter, quando para a direita, adiciona 1.
    criar_codigos(node.left, current_code + "0", codes)
    criar_codigos(node.right, current_code + "1", codes)
    return codes

def codificar(text, codes):
    '''
    Recebe um texto e o dicionário dos códigos e retorna o texto
    codificado.
    
    Parâmetros:
    text: texto para ser codificado para binário.
    codes: códigos de cada caráter presente no texto.

    Retorna:
    O texto codificado.
    '''
    # Vai retornar uma string com o código de cada letra (caráter) 
    # no lugar dos caráteres do texto.
    return ''.join(codes[char] for char in text)

def decodificar(encoded_text, tree):

    '''
    Recebe o texto codificado em binário e a árvore de huffman.

    Parâmetros:
    encoded_text: texto codificado em binário.
    tree: a árvore utilizada para codificar.
    
    Retorna:
    O texto descodificado.
    '''

    decodificado = ''
    node = tree
    for bit in encoded_text:
        # Para cada bit do texto, anda ná árvore pra esquerda (se 0)
        # ou pra direita (se 1)
        node = node.left if bit == '0' else node.right
        # Se caminhar para None, significa que adiciona o caráter
        # do nó atual ao texto decodificado
        if node.char is not None:
            decodificado += node.char
            # Deve-se definir novamente o nó raiz para fazer o procedimento
            # com os outros bits
            node = tree
    return decodificado

def serializar_arvore(node):
    if node.char is not None:
        return '1' + f'{ord(node.char):08b}'  # folha: flag 1 + 8 bits do caractere
    return '0' + serializar_arvore(node.left) + serializar_arvore(node.right)  # interno: flag 0

def desserializar_arvore(bits_iter):
    try:
        flag = next(bits_iter)
    except StopIteration:
        return None

    if flag == '1':
        char_bits = ''.join(next(bits_iter) for _ in range(8))
        char = chr(int(char_bits, 2))
        return Node(char=char)
    else:
        left = desserializar_arvore(bits_iter)
        right = desserializar_arvore(bits_iter)
        node = Node()
        node.left = left
        node.right = right
        return node
    
def bits_para_bytes(bits: str) -> bytes:
    # Preenche para múltiplo de 8 bits (se necessário)
    padding = 8 - len(bits) % 8 if len(bits) % 8 != 0 else 0
    bits += '0' * padding
    byte_array = bytearray()

    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        byte_array.append(int(byte, 2))

    return bytes([padding]) + bytes(byte_array)  # Primeiro byte = padding

def bytes_para_bits(data: bytes) -> str:
    padding = data[0]
    bitstring = ''.join(f'{byte:08b}' for byte in data[1:])
    return bitstring[:-padding] if padding else bitstring

def salvar(filename, encoded_text, tree):
    arvore_bits = serializar_arvore(tree)
    arvore_bytes = bits_para_bytes(arvore_bits)
    dados_bytes = bits_para_bytes(encoded_text)

    with open(filename, 'wb') as f:
        f.write(len(arvore_bytes).to_bytes(4, 'big'))  # Tamanho da árvore (4 bytes)
        f.write(arvore_bytes)  # Árvore serializada
        f.write(dados_bytes)   # Dados comprimidos

def carregar(filename):
    with open(filename, 'rb') as f:
        tam_arvore = int.from_bytes(f.read(4), 'big')         # Lê tamanho da árvore
        arvore_bytes = f.read(tam_arvore)                     # Lê árvore
        dados_bytes = f.read()                                # Lê o restante (dados)

    arvore_bits = bytes_para_bits(arvore_bytes)
    bits_iter = iter(arvore_bits)
    tree = desserializar_arvore(bits_iter)

    encoded_text = bytes_para_bits(dados_bytes)
    return encoded_text, tree

def desenhar_arvore(tree, filename="huffman_tree"):
    dot = Digraph()
    node_id = [0]

    def add_nodes(node, parent_id=None, label=""):
        if node is None:
            return
        curr_id = str(node_id[0])
        node_id[0] += 1

        node_label = f"'{node.char}'\n{node.freq}" if node.char else f"{node.freq}"
        dot.node(curr_id, node_label)

        if parent_id is not None:
            dot.edge(parent_id, curr_id, label=label)

        add_nodes(node.left, curr_id, "0")
        add_nodes(node.right, curr_id, "1")

    add_nodes(tree)
    dot.render(filename, format='png', cleanup=True)
    os.startfile(f"{filename}.png") 

# ------------------------------------------------------------------
# Definição das funções da interface gráfica
def compactar():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if not file_path:
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    freq_table = dic_freq(text)
    tree = arvore_huffman(freq_table)
    codes = criar_codigos(tree)
    encoded_text = codificar(text, codes)
    encoded_text_path = file_path.replace(".txt","_encoded.txt")

    with open(encoded_text_path, 'w') as f:
        f.write(encoded_text)
    compressed_path = file_path.replace(".txt",".huff")
    salvar(compressed_path, encoded_text, tree)

    desenhar_arvore(tree)

    messagebox.showinfo("Compactação concluída", f"Arquivo compactado salvo em:\n{compressed_path}")

def descompactar():
    file_path = filedialog.askopenfilename(filetypes=[("Huffman files", "*.huff")])
    if not file_path:
        return

    encoded_text, tree = carregar(file_path)
    decoded_text = decodificar(encoded_text, tree)

    original_path = file_path.replace(".huff", "_restored.txt")
    with open(original_path, 'w', encoding='utf-8') as f:
        f.write(decoded_text)

    messagebox.showinfo("Descompactação concluída", f"Texto restaurado salvo em:\n{original_path}")

# ------------------------------------------------------------------------
# Execução do programa
root = Tk()
root.title("Compactador Huffman")
root.geometry("400x200")

Label(root, text="Compactador de Huffman", font=("Arial", 16)).pack(pady=10)

Button(root, text="Compactar Arquivo .txt", command=compactar, width=30).pack(pady=10)
Button(root, text="Descompactar Arquivo .huff", command=descompactar, width=30).pack(pady=10)

root.mainloop()
