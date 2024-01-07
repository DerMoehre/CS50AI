import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    probability_dict = dict()
    # calculate difference 1-damping
    difference = 1 - damping_factor
    
    # get number of pages
    number = len(corpus[page])
    
    # case: page has no outgoing link
    if number == 0:
        number = len(corpus)
        probability = damping_factor / number
        add_probability = (difference / (number))
        for item in corpus:
            probability_dict.update({item: probability + add_probability})
    else:
        probability = damping_factor / number
        add_probability = (difference / (number + 1))
    
        probability_dict.update({page: add_probability})
    
        for item in corpus[page]:
            probability_dict.update({item: probability + add_probability})
    
    return probability_dict
    
def get_weighted_choice(distribution):
    page = []
    probability = []
    
    for key, value in distribution.items():
        page.append(key)
        probability.append(value)
    
    return random.choices(page, weights=probability, k=1)[0]

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # initialise dictionary
    page_rank = dict()
    for page in corpus:
        page_rank.update({page: 0})
        
    # get initial page
    initial = random.choice(list(corpus.keys()))
    
    for i in range(n):
        if i == 0:
            distribution = transition_model(corpus, initial, damping_factor)
            choice = get_weighted_choice(distribution)
        distribution = transition_model(corpus, choice, damping_factor)
        choice = get_weighted_choice(distribution)
        page_rank[choice] = page_rank.get(choice) + 1/n
    return page_rank
        
        
def get_links(corpus, page):
    return list(corpus[page])

def get_internal_links(corpus, page):
    internal_links = []
    for element in corpus:
        if page in corpus[element]:
            internal_links.append(element)
    return internal_links

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    calculating = True
    
    # first half of equation
    first_half = (1-damping_factor) / len(corpus)
    
    # initial page_rank
    page_rank = dict()
    temp_rank = dict()
    check_dict = dict()
    for page in corpus:
        page_rank.update({page: 1/len(corpus)})

    while calculating:
        for page in corpus:
            sum_function = 0
            # get links to the website
            page_links = get_internal_links(corpus, page)
            if len(page_links) == 0:
                page_links = list(corpus.keys())
            for link in page_links:
                # calculating the sum with corresponding outgoing links
                sum_function += page_rank[link] / len(get_links(corpus, link))
            temp_rank.update({page: first_half + damping_factor*sum_function})
            
        # check the difference
        check_dict.update({k: abs(page_rank[k] - temp_rank[k]) for k in page_rank})  
        
        if all(x < 0.001 for x in check_dict.values()):
            calculating = False
            return page_rank
        
        page_rank.update({k: temp_rank[k] for k in page_rank}) 
        
    
    
    
if __name__ == "__main__":
    main()
