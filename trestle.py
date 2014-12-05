import json
from cobweb3 import Cobweb3Tree, Cobweb3Node
from structure_mapper import flatMatch, renameFlat, flattenJSON

class TrestleTree(Cobweb3Tree):

    def __init__(self):
        self.root = Cobweb3Node()

    def ifit(self, instance):
        """
        A modification of ifit to call Trestle instead.
        """
        return self.trestle(instance)

    def trestle_categorize(self, instance):
        """
        The Trestle categorize function, this Trestle categorizes all the
        sub-components before categorizing itself.
        """
        temp_instance = flattenJSON(instance)
        mapping = flatMatch(self.root, temp_instance)
        temp_instance = renameFlat(temp_instance, mapping)
        return self.cobweb_categorize(temp_instance)

    def trestle(self, instance):
        """
        Recursively calls Trestle on all of the components in a depth-first
        traversal. Once all of the components have been classified then then it
        classifies the current node.
        """
        temp_instance = flattenJSON(instance)
        mapping = flatMatch(self.root, temp_instance)
        temp_instance = renameFlat(temp_instance, mapping)
        return self.cobweb(temp_instance)

if __name__ == "__main__":

    # KC labeling
    tree = TrestleTree()

    with open('data_files/rb_s_07_continuous.json', "r") as json_data:
        instances = json.load(json_data)
    print(len(instances))
    #instances = instances[0:20]
    print(set(tree.cluster(instances)))

    #labels = tree.kc_label("data_files/instant-test-processed.json", 16000)
    #pickle.dump(labels, open('clustering.pickle', 'wb'))



