import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count and self.count > 0:
            return self.cells

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.difference_update(set([cell]))
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        
        if cell in self.cells:
            self.cells.difference_update(set([cell]))
      

class MinesweeperAI():
    """
    Minesweeper game player
    """
    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.update(cell)
        for sentence in self.knowledge:
           sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)
            if len(sentence.cells) == sentence.count:
                self.mark_mine(sentence.cells)
                self.knowledge.remove(sentence)

    def find_neighbors(self, cell):
        # get cell position
        neighbor = []
        row = cell[0]
        column = cell[1]

        # calculate the surrounding cell coordinates
        for i in range(-1,2):
            for j in range(-1,2):
                if i == 0 and j == 0:
                    continue
                if row + i >= self.height or column + j >= self.width or row + i < 0 or column + j < 0:
                    continue
                neighbor.append((row + i, column + j))
        return neighbor
    
    def check_sentence(self):
        for sentence in self.knowledge:
            for next_sentence in self.knowledge:
                if len(next_sentence.cells) <= len(sentence.cells):
                    if next_sentence.cells.issubset(sentence.cells) and (next_sentence != sentence):
                        add_sentence = next_sentence.cells.symmetric_difference(sentence.cells)
                        add_count = sentence.count - next_sentence.count
                        if add_count == 0:
                            for item in add_sentence:
                                self.mark_safe(item)
                            continue
                        if add_count == len(add_sentence):
                            for item in add_sentence:
                                self.mark_mine(item)
                            continue
                        new_sentence = Sentence(add_sentence, add_count)
                        if new_sentence in self.knowledge:
                            continue
                        self.knowledge.append(new_sentence)
                else:
                    if sentence.cells.issubset(next_sentence.cells) and (next_sentence != sentence):
                        add_sentence = sentence.cells.symmetric_difference(next_sentence.cells)
                        add_count = next_sentence.count - sentence.count
                        if add_count == 0:
                            for item in add_sentence:
                                self.mark_safe(item)
                            continue
                        if add_count == len(add_sentence):
                            for item in add_sentence:
                                self.mark_mine(item)
                            continue
                        new_sentence = Sentence(add_sentence, add_count)
                        if new_sentence in self.knowledge:
                            continue
                        self.knowledge.append(new_sentence)
                        
            

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # adding cell coordinates to set
        self.moves_made.add(cell)

        # mark cell as save
        self.mark_safe(cell)

        # finding surrounding cells
        neighbors = self.find_neighbors(cell)
        
        # remove known safe cells from neighbors
        for item in self.safes:
            if item in neighbors:
                neighbors.remove(item)

        # remove known mines from neighbors
        for item in self.mines:
            if item in neighbors:
                neighbors.remove(item)
                count -= 1

        if count == 0:
            for item in neighbors:
                self.mark_safe(item)
        elif len(neighbors) == count:
            for item in neighbors:
                self.mark_mine(set([(item)]))
        # adding new sentence to knowledge
        else:
            new_sentence = Sentence(neighbors, count)
            self.knowledge.append(new_sentence)
            self.check_sentence()
            

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        possible_safe_moves = self.moves_made.symmetric_difference(self.safes)
        print(f"possible safe moves: {len(possible_safe_moves)}")
        if len(possible_safe_moves) == 0:
            return None
        return next(iter(possible_safe_moves))

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # create board cells
        board = set()
        for row in range(0, self.height):
            for column in range(0, self.width):
                board.add((row, column))
        # cancel all known moves and mines
        unclicked = board.symmetric_difference(self.moves_made)
        unclicked_safe = unclicked.symmetric_difference(self.mines)
        print(f"len unclicked safe: {len(unclicked_safe)}")
        if len(unclicked_safe) > 0:
            return next(iter(unclicked_safe))
        return None
