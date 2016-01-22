# Author:   Adam Anderson
# Date:     Jan 6, 2015
# Updated:  Jan 21, 2016
# Python:   3.4+


class TextNode(object):

    def __init__(self, parent, text):
        """ Constructs a new TextNode.

            parent - a TextNode that is the parent of this one.  Must not be
                     None.
            text   - a String containing the text for this node. Must not be
                     None.
        """

        # Init Members
        # --- The Real Data
        self.text = text
        self.usages = 0
        if text:
            self.usages += 1

        # --- Navigation / Tree MetaData        
        self.parent = parent
        self.children = {}
        self.depth = 0
        if self.parent is not None:
            self.depth = parent.depth + 1

    def add_text(self, word_list):
        if word_list:
            # pop first word out of list and create this Node's new child node
            word = word_list.pop(0)

            # recursively process the remaining words in the list
            # if the node for this word already exists, update it and keep going.
            if word in self.children.keys():
                node = self.children[word]
                node.usages += 1
                node.add_text(word_list)
            else:
                # if not, create a new node, and keep going.
                next_node = TextNode(self, word)
                self.children[word] = next_node
                next_node.add_text(word_list)

    def add_child(self, node):
        """ Adds a new child node to this Text Node.
            node - a TextNode to add as a child to this node.
        """
        self.children[node.text] = node

    def dump(self):
        print("text:", self.text, ", usages:", str(self.usages), ", depth:", str(self.depth))
        for node in self.children.values():
            node.dump()


class TextTree(object):

    def __init__(self):
        self.root = TextNode(None, None)
        self.root.usages = -1

    def add_text(self, sentence):
        self.root.add_text(self.__sanitize(sentence))

    def dump_data(self):
        self.root.dump()

    def __sanitize(self, sentence):
        """ A crude attempt at text sanitization. """
        # remove punctuation
        sentence = sentence.replace(",", "")
        sentence = sentence.replace(":", "")
        sentence = sentence.replace(";", "")
        
        # Determine if any final punctuation exists
        words = []
        if sentence.endswith("."):
            sentence = sentence[:-1]
            words += sentence.split()
            words.append(".")
        elif sentence.endswith("?"):
            sentence = sentence[:-1]
            words += sentence.split()
            words.append("?")
        elif sentence.endswith("!"):
            sentence = sentence[:-1]
            words += sentence.split()
            words.append("!")

        return words
            

def main():
    tree = TextTree()
    tree.add_text("Hello, world!")
    tree.add_text("Hello, mom.")
    tree.add_text("Hello, I love you won't you tell me your name.")
    tree.add_text("Yeah, I'm on my way.")
    tree.dump_data()


if __name__ == "__main__":
    main()