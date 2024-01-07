import sys
import itertools

from crossword import Crossword, Variable


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # remove those words from set, which are not the correct length
        for key, value in self.domains.items():
            remove = set()
            for item in value:
                if len(item) != key.length:
                    remove.add(item)
            value.difference_update(remove)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        overlap = self.crossword.overlaps[x, y]
        delete = set()
        if overlap is None:
            return revised
        x_overlap, y_overlap = overlap
        for x_word in self.domains[x]:
            found = 0
            for y_word in self.domains[y]:
                if x_word[x_overlap] != y_word[y_overlap]:
                    found += 1
            if found == len(self.domains[y]):
                delete.add(x_word)
                revised = True
        self.domains[x].difference_update(delete)
        
        return revised
            
    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            arcs = list(itertools.combinations(self.domains, 2))
        
        while arcs:
            X, Y = arcs.pop(0)
            if self.revise(X, Y):
                if len(self.domains[X]) == 0:
                    return False
                for Z in self.crossword.neighbors(X) - {Y}:
                    arcs.append((Z, X))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(assignment) == len(self.domains.keys()):
            return True
        return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for key, value in assignment.items():
            # check for equal length in needed spot and given word
            if key.length != len(value):
                return False
                # check for conflicts at neighbors
            for neighbor in self.crossword.neighbors(key):
                if neighbor in assignment:
                    if self.crossword.overlaps[key, neighbor]:
                        key_overlap, neighbor_overlap = self.crossword.overlaps[key, neighbor]
                        if value[key_overlap] != assignment[neighbor][neighbor_overlap]:
                                return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # get neighboring cells
        neighbors = self.crossword.neighbors(var)
        # delete the cells in assignment from neighbors
        unassigned_neighbors = neighbors - set(assignment.keys())
        domain = {}
        # loop over the words in cell
        for value in self.domains[var]:
            found = 0
            # check every neighbor
            for neighbor in unassigned_neighbors:
                for n_value in self.domains[neighbor]:
                    # check if cells overlap and split the tuple
                    if self.crossword.overlaps[var, neighbor]:
                        key_overlap, neighbor_overlap = self.crossword.overlaps[var, neighbor]
                        # if the words dont match, the counter goes up
                        # a higher counter indicates a higher number of out ruled words
                        if value[key_overlap] != n_value[neighbor_overlap]:
                            found += 1
            domain[value] = found
        # sort values by found counter
        ordered_domain = sorted(domain, key= domain.get)
        return ordered_domain

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        len_values = 5000
        return_key = ""
        for key, value in self.domains.items():
            if key not in assignment:
                if len(value) < len_values:
                    len_values = len(self.domains[key])
                    return_key = key
                if len(value) == len_values:
                    if len(self.crossword.neighbors(key)) > len(self.crossword.neighbors(return_key)):
                        return_key = key
        return return_key
                
    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            temp_assignment = assignment.copy()      
            temp_assignment.update({var: value})
            if self.consistent(temp_assignment):
                assignment.update({var: value})
                result = self.backtrack(assignment)
                if result != None:
                    return result
                assignment.popitem()
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
