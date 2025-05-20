# huffman.py
import os
import pickle
from tkinter import filedialog, messagebox, Tk, Button, Label
from graphviz import Digraph
import os

class HuffmanNode:
    def __init__(self, char=None, freq=0):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def build_frequency_table(text):
    freq = {}
    for char in text:
        freq[char] = freq.get(char, 0) + 1
    return dict(sorted(freq.items(), key=lambda item: item[1]))


def build_huffman_tree(freq_table):
    heap = [HuffmanNode(char, freq) for char, freq in freq_table.items()]
    while len(heap) > 1:

        heap.sort(key=lambda node: node.freq)
        node1 = heap.pop(0)
        node2 = heap.pop(0)
        merged = HuffmanNode(None, node1.freq + node2.freq)
        merged.left = node1
        merged.right = node2
        heap.append(merged)

    return heap[0]


def build_codes(node, current_code="", codes={}):
    if node is None:
        return

    if node.char is not None:
        codes[node.char] = current_code

    build_codes(node.left, current_code + "0", codes)
    build_codes(node.right, current_code + "1", codes)
    return codes

def encode(text, codes):
    return ''.join(codes[char] for char in text)

def decode(encoded_text, tree):
    decoded = ''
    node = tree
    for bit in encoded_text:
        node = node.left if bit == '0' else node.right
        if node.char is not None:
            decoded += node.char
            node = tree
    return decoded

def save_compressed_file(filename, encoded_text, tree):
    with open(filename, 'wb') as f:
        pickle.dump((encoded_text, tree), f)

def load_compressed_file(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)

def draw_huffman_tree(tree, filename="huffman_tree"):
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

def compact_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if not file_path:
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    freq_table = build_frequency_table(text)
    tree = build_huffman_tree(freq_table)
    codes = build_codes(tree)
    encoded_text = encode(text, codes)

    compressed_path = file_path + ".huff"
    save_compressed_file(compressed_path, encoded_text, tree)

    draw_huffman_tree(tree)

    messagebox.showinfo("Compactação concluída", f"Arquivo compactado salvo em:\n{compressed_path}")

def decompress_file():
    file_path = filedialog.askopenfilename(filetypes=[("Huffman files", "*.huff")])
    if not file_path:
        return

    encoded_text, tree = load_compressed_file(file_path)
    decoded_text = decode(encoded_text, tree)

    original_path = file_path.replace(".huff", "_restored.txt")
    with open(original_path, 'w', encoding='utf-8') as f:
        f.write(decoded_text)

    messagebox.showinfo("Descompactação concluída", f"Texto restaurado salvo em:\n{original_path}")

# ------------------------------------------------------------------------

root = Tk()
root.title("Compactador Huffman")
root.geometry("400x200")

Label(root, text="Compactador de Huffman", font=("Arial", 16)).pack(pady=10)

Button(root, text="Compactar Arquivo .txt", command=compact_file, width=30).pack(pady=10)
Button(root, text="Descompactar Arquivo .huff", command=decompress_file, width=30).pack(pady=10)

root.mainloop()
