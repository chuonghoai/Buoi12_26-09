import tkinter as tk
from PIL import Image, ImageTk
import random

class node:
    def __init__(self, n=8):
        self.n = n
        self.state = []
        self.cost = 0

    def cost_conflict(self, state=None):
        if state == None:
            state = self.state
        cnt = 0
        for i in range(self.n):
            for j in range(i + 1, len(state)):
                if state[i] == state[j]:
                    cnt += 1
        return cnt
    
class Image_X:
    def __init__(self):
        self.white = ImageTk.PhotoImage(Image.open("./whiteX.png").resize((60, 60)))
        self.black = ImageTk.PhotoImage(Image.open("./blackX.png").resize((60, 60)))
        self.null = tk.PhotoImage(width=1, height=1)
        
class board:
    def __init__(self, root):  #n: số lượng quân xe (defult = 8)
        self.root = root
        root.title("Simulated Anneling")
        root.config(bg="lightgray")
        self.image = Image_X()
        self.n = node().n
        
        self.frame_path = self.draw_frame(0, 0)
        self.text_path = tk.Text(self.frame_path, width=25, height=31)
        self.text_path.pack(anchor="nw", padx=5, pady=5)
        
        self.frame_left = self.draw_frame(0, 1)
        self.frame_right = self.draw_frame(0, 2)
        self.board_left = self.create_board(self.frame_left)
        self.board_right = self.create_board(self.frame_right)
        self.draw_button()
        
    def draw_frame(self, row, col, background="white", rl="solid", border=1, HLthickness=1):
        frame = tk.Frame(self.root, bg=background, relief=rl, bd=border, highlightthickness=HLthickness)
        frame.grid(column=col, row=row, padx=10, pady=10)
        return frame
    
    def create_board(self, frame):
        buttons = []
        for i in range(self.n):
            row = []
            for j in range(self.n):
                color = "white" if (i + j) % 2 == 0 else "black"
                img = self.image.null                
                btn = tk.Button(frame, image=img, width=60, height=60, bg=color,
                                relief="flat", borderwidth=0, highlightthickness=0)
                btn.grid(row = i, column = j, padx=1, pady=1)
                row.append(btn)
            buttons.append(row)
        return buttons

    def draw_button(self):
        _pady = 5
        _padx = 10
        _width = 20
        
        frame_button_left = self.draw_frame(1, 1, "lightgray", "flat", 0, 0)
        frame_button_right = self.draw_frame(1, 2, "lightgray", "flat", 0, 0)
        
        self.and_or_btn = tk.Button(frame_button_right, text="And - Or search trees", width=_width)
        self.and_or_btn.grid(row=1, column=1, pady=_pady, padx=_padx)
        self.belief_btn = tk.Button(frame_button_right, text="Belief search", width=_width)
        self.belief_btn.grid(row=2, column=1, pady=_pady, padx=_padx)
        
        self.reset_btn = tk.Button(frame_button_left, text="Reset", bg="red", fg="white")
        self.reset_btn.grid(row=1, column=1, pady=_pady, padx=_padx)
        self.path_btn = tk.Button(frame_button_left, text="Path")
        self.path_btn.grid(row=1, column=0, pady=_pady, padx=_padx)

    def draw_xa(self,  buttons, state=[]):
        for i in range(self.n):
            for j in range(self.n):
                buttons[i][j].config(image=self.image.null)
        
        for row, col in enumerate(state):
            color = "white" if (row + col) % 2 == 0 else "black"
            img = self.image.white if color == "black" else self.image.black
            buttons[row][col].config(image=img)

class algorithm(board):
    def __init__(self, root):
        super().__init__(root)
        self.reset_btn.config(command=self.reset)
        self.path_btn.config(command=self.path)
        
        self.and_or_btn.config(command=self.and_or_btn_algorithm)
        self.belief_btn.config(command=self.belief_search_btn_algorithm)
        
        self.path_state = []
        self.setting_xa = True
        
    def reset(self):
        self.setting_xa = False
        self.path_state = []
        self.text_path.delete("1.0", tk.END)
        self.draw_xa(self.board_left)
        self.draw_xa(self.board_right)

    def path(self):
        if not self.setting_xa:
            self.setting_xa = True
        self.text_path.delete("1.0", tk.END)
        for state in self.path_state:
            if not self.setting_xa:
                return
            self.draw_xa(self.board_left, state)
            self.text_path.insert(tk.END, str(state) + "\n")
            self.text_path.see(tk.END)
            self.frame_left.update()
            self.root.after(200)
            
    # --------------------- AND-OR TREE SEARCH -------------------------
    def and_or_algorithm(self):
        return self.or_search([], [])

    def or_search(self, state, path):
        if len(state) == self.n:
            return []
        if state in path:
            return None

        for col in self.free_col(state):
            child = [(state + [col])]
            plan = self.and_search(child, path + [state])
            if plan is not None:
                return [(col, plan)]
        return None

    def and_search(self, states, path):
        plans = []
        for s in states:
            plan = self.or_search(s, path)
            if plan is None:
                return None
            plans.append((s, plan))
        return plans
    
    def free_col(self, state):
        used = {c for c in state}
        return [c for c in range(self.n) if c not in used]
    
    def extract_solution(self, plan):
        state = []
        while plan:
            _, outcomes = plan[0]
            state_next, subplan = outcomes[0]
            state = state_next
            plan = subplan
            self.path_state.append(state)
        return state
    
    def and_or_btn_algorithm(self):
        self.path_state = []
        self.draw_xa(self.board_left)
        self.draw_xa(self.board_right)
        
        plan = None
        while plan is None:
            plan = self.and_or_algorithm()
        state = self.extract_solution(plan)
        self.draw_xa(self.board_right, state)
        
    # ------------------------------------------------------------------
    
    # --------------------- Belief state search ------------------------    (trạng thái niềm tin)
    def belief_search(self, list_start_state=[]): 
        if list_start_state == []: 
            list_state = [[]] 
        else: 
            list_state = [s for s in list_start_state if self.valid_state(s)] 
        while list_state: 
            new_list_state = []
            for state in list_state: 
                flag = False
                self.path_state.append(state)
                if len(state) == self.n: 
                    return state 
                
                for col in self.free_col(state): 
                    child = state + [col] 
                    if self.valid_state(child): 
                        new_list_state.append(child)
                        break
            list_state = new_list_state 
        return None
    
    def valid_state(self, state):
        return len(state) == len(set(state))

    def find_conflict(self, state):
        used = set()
        for i, col in enumerate(state):
            if col in used:
                return i
            used.add(col)
        return None

    def random_start_state(self):
        n_stage = random.randint(1, int(self.n/2))
        start_state = []
        for _ in range(n_stage):
            n_num = random.randint(0, int(self.n/2))
            state = [random.randint(0, self.n - 1) for _i in range(n_num)]
            start_state.append(state)
        return start_state

    def belief_search_btn_algorithm(self):
        self.path_state = []
        self.draw_xa(self.board_left)
        self.draw_xa(self.board_right)
        
        state = None
        print("Các trạng thái hệ thống cho rằng đang đứng hiện tại: ")
        start_st = self.random_start_state()
        print(start_st)
        while state is None:
            state = self.belief_search(start_st)
        self.draw_xa(self.board_right, state)
    # ------------------------------------------------------------------
    

def run_app():
    root = tk.Tk()
    app = algorithm(root)
    root.mainloop()

if __name__ == "__main__":
    run_app()