import sys
import ast
import re
import collections

from collections import OrderedDict

def spimi_blocks(documents, block_size_limit):
    block_number = 0
    documents_count = len(documents)
    dictionary = {} # (term - postings list)
    for index, doc in enumerate(documents):
        for term in doc["content"]:
            # If term occurs for the first time
            if term not in dictionary.keys():
                # Add term to dictionary, create new postings list, and add docID
                dictionary[term] = set()
            dictionary[term].add(index)
        if sys.getsizeof(dictionary) > block_size_limit or (index == documents_count-1):
            temp_dict = sort_terms(dictionary) # so that merging is easy
            write_block_to_disk(temp_dict, block_number)
	    print "wrote block", block_number, " ", index/documents_count*100,"% complete"
            temp_dict = {}
            block_number += 1
            dictionary = {}
    print("SPIMI invert complete!")

def sort_terms(term_postings_list):
    """ Sorts dictionary terms in alphabetical order """
    print(" -- Sorting terms...")
    sorted_dictionary = OrderedDict() # keep track of insertion order
    sorted_terms = sorted(term_postings_list.keys())
    for term in sorted_terms:
        sorted_dictionary[term] = [int(docIds) for docIds in term_postings_list[term]]
    return sorted_dictionary


def write_block_to_disk(term_postings_list, block_number):
    """ Writes index of the block (dictionary + postings list) to disk """
    # Define block
    base_path = 'index_blocks/'
    block_name = 'block-' + str(block_number) + '.txt'
    block = open(base_path + block_name, 'a+')
    print(" -- Writing term-positing list block: " + block_name + "...")
    # Write term : posting lists to block
    for term in term_postings_list.keys():
        # Term - Posting List Format
        # term:[docID1, docID2, docID3]
        # e.g. cat:[4,9,21,42]
        block.write(str(term) + ":" + str((term_postings_list[term])) + "\n")
    block.close()

def merge_blocks(blocks):
    """ Merges SPIMI blocks into final inverted index """
    print "--Merging Blocks--"
    merge_completed = False
    spimi_index = open('spimi_inverted_index.txt', 'a+')
    # Collect initial pointers to (term : postings list) entries of each SPIMI blocks
    temp_index = OrderedDict()
    for num, block in enumerate(blocks):
        print("-- Reading into memory...", block.name)
        line = block.readline() # first term in each block (term:[docID1, docID2, docID3])
        line_tpl = line.rsplit(':', 1)
        term = line_tpl[0]
        postings_list = ast.literal_eval(line_tpl[1])
        temp_index[num] = {term:postings_list}
	#print temp_index[num]
    while not merge_completed:
        # Convert into an array of [{term: [postings list]}, blockID]
        tpl_block = ([[temp_index[i], i] for i in temp_index])
        # Fetch the current term postings list with the smallest alphabetical term
        smallest_tpl = min(tpl_block, key=lambda t: list(t[0].keys()))
        # Extract term
        smallest_tpl_term = (smallest_tpl[0].keys())[0]
        # Fetch all IDs of blocks that contain the same term in their currently pointed (term: postings list) :
        # For each block, check if the smallest term is in the array of terms from all blocks then extract the block id
        smallest_tpl_block_ids = [block_id for block_id in temp_index if smallest_tpl_term in [term for term in temp_index[block_id].keys()]]
        # Build a new postings list which contains all postings related to the current smallest term
        # Flatten the array of postings and sort
        smallest_tpl_pl =(sorted(sum([pl[smallest_tpl_term] for pl in (temp_index[block_id] for block_id in smallest_tpl_block_ids)], [])))
	print str(smallest_tpl_term) + ":" + str(smallest_tpl_pl) + "\n"
        spimi_index.write(str(smallest_tpl_term) + ":" + str(smallest_tpl_pl) + "\n")
#Need to Debug
        # Collect the next sectioned (term : postings list) entries from blocks that contained the previous smallest tpl term
        for block_id in smallest_tpl_block_ids:
            # Read the blocks and read tpl in a temporary index
            block = [fil for fil in blocks if re.search('block-'+str(block_id), fil.name)]
            if block[0]:
                line = block[0].readline()
                if not line == '':
                    line_tpl = line.rsplit(':', 1)
                    term = line_tpl[0]
                    postings_list = ast.literal_eval(line_tpl[1])
                    temp_index[block_id] = {term:postings_list}
                else:
                    # Delete block entry from the temporary sectioned index holder if no line found
                    del temp_index[block_id]
                    blocks.remove(block[0])
                    print("Finished merging block:", block[0].name)
            else:
                blocks.remove(block[0])
        # If all block IO streams have been merged
        if not blocks:
            merge_completed = True
            print("SPIMI completed! All blocks merged into final index: spimi_inverted_index.txt")
	return 0
