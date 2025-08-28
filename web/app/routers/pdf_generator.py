from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from fpdf import FPDF
import random
import os
import uuid

router = APIRouter()

# --- Constants and Setup ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, '..', 'fonts', 'NotoSansSC-Regular.ttf')
TMP_DIR = os.path.join(BASE_DIR, '..', 'tmp')
os.makedirs(TMP_DIR, exist_ok=True)

# --- PDF Class ---
class PDF(FPDF):
    def header(self):
        if not os.path.exists(FONT_PATH):
            self.set_font('Arial', 'B', 15)
            self.cell(0, 10, 'Math Problems', 0, 1, 'C')
            return
        
        self.add_font('NotoSansSC', '', FONT_PATH)
        self.set_font('NotoSansSC', '', 15)
        title = self.title or 'Math Problems'
        self.cell(0, 10, title, 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

# --- Problem Generation Logic ---
def generate_problems(problem_type: str, max_number: int, num_operands: int, operators: str, num_problems: int, op_mode: str):
    problems = []
    op_map = {
        'add_subtract': ['+', '-'],
        'multiply_divide': ['*', '/'],
        'all': ['+', '-', '*', '/']
    }
    allowed_ops = op_map.get(operators, ['+', '-'])

    sequential_count = 0
    max_sequential = num_problems // 10  # 10% limit

    for _ in range(num_problems):
        problem_generated = False
        while not problem_generated:
            try:
                # --- Operator Generation ---
                ops = []
                if num_operands > 1:
                    if op_mode == 'mixed' and num_operands > 2:
                        while True:
                            ops = [random.choice(allowed_ops) for _ in range(num_operands - 1)]
                            is_sequential = len(set(ops)) == 1
                            if is_sequential:
                                if sequential_count < max_sequential:
                                    sequential_count += 1
                                    break
                                else:
                                    continue
                            else:
                                break
                    else:
                        op = random.choice(allowed_ops)
                        ops = [op] * (num_operands - 1)

                # --- Operand and Problem Generation ---
                if problem_type == 'simple_calculation':
                    if num_operands < 2: continue
                    
                    nums = [0] * num_operands
                    calculation_limit = max_number * 10
                    current_value = random.randint(1, max_number)
                    nums[0] = current_value

                    for i, op in enumerate(ops):
                        if op == '+':
                            max_add = max(1, calculation_limit - current_value)
                            next_val = random.randint(1, max_add)
                            current_value += next_val
                            nums[i+1] = next_val
                        elif op == '-':
                            next_val = random.randint(1, current_value) if current_value > 0 else 0
                            current_value -= next_val
                            nums[i+1] = next_val
                        elif op == '*':
                            if current_value == 0:
                                next_val = random.randint(1, max_number)
                            else:
                                max_multiplier = max(2, calculation_limit // current_value) if current_value > 0 else calculation_limit
                                next_val = random.randint(1, max_multiplier)
                            current_value *= next_val
                            nums[i+1] = next_val
                        elif op == '/':
                            if current_value == 0:
                                next_val = random.randint(1, max_number)
                            else:
                                divisors = [j for j in range(1, current_value + 1) if current_value % j == 0]
                                if not divisors:
                                    continue
                                next_val = random.choice(divisors)
                                current_value //= next_val
                            nums[i+1] = next_val
                    
                    problem_str = str(nums[0])
                    for i, op in enumerate(ops):
                        if op == '/':
                            problem_str += f" ÷ {nums[i+1]}"
                        elif op == '*':
                            problem_str += f" × {nums[i+1]}"
                        else:
                            problem_str += f" {op} {nums[i+1]}"
                    problems.append(f"{problem_str} = ")
                    problem_generated = True

                elif problem_type == 'find_missing_number':
                    nums = [0] * num_operands
                    calculation_limit = max_number * 10
                    current_value = random.randint(0, max_number)
                    nums[0] = current_value

                    for i, op in enumerate(ops):
                        if op == '+':
                            max_add = max(1, calculation_limit - current_value)
                            next_val = random.randint(0, max_add)
                            current_value += next_val
                            nums[i+1] = next_val
                        elif op == '-':
                            next_val = random.randint(0, current_value) if current_value > 0 else 0
                            current_value -= next_val
                            nums[i+1] = next_val
                        elif op == '*':
                            if current_value == 0:
                                next_val = random.randint(1, max_number)
                            else:
                                max_multiplier = max(2, calculation_limit // current_value) if current_value > 0 else calculation_limit
                                next_val = random.randint(1, max_multiplier)
                            current_value *= next_val
                            nums[i+1] = next_val
                        elif op == '/':
                            if current_value == 0:
                                next_val = random.randint(1, max_number)
                            else:
                                divisors = [j for j in range(1, current_value + 1) if current_value % j == 0]
                                if not divisors:
                                    continue
                                next_val = random.choice(divisors)
                                current_value //= next_val
                            nums[i+1] = next_val
                    final_result = current_value

                    missing_pos = random.randint(0, num_operands - 1)
                    problem_str = ""
                    for i in range(num_operands):
                        if i == missing_pos:
                            problem_str += "▢"
                        else:
                            problem_str += str(nums[i])
                        
                        if i < len(ops):
                            if ops[i] == '/':
                                problem_str += "÷"
                            elif ops[i] == '*':
                                problem_str += "×"
                            else:
                                problem_str += f" {ops[i]} "
                    problems.append(f"{problem_str} = {final_result}")
                    problem_generated = True

            except (ValueError, ZeroDivisionError, OverflowError):
                continue

    return problems

# --- API Endpoint ---
@router.get("/api/generate-pdf")
def generate_pdf(problem_type: str, max_number: int = 20, num_operands: int = 2, operators: str = 'add_subtract', num_problems: int = 50, op_mode: str = 'mixed'):
    if not os.path.exists(FONT_PATH):
        print(f"WARNING: Font file not found at {FONT_PATH}. Using fallback font.")

    # --- Title Generation ---
    type_title_map = {'simple_calculation': "常规计算", 'find_missing_number': "带未知数的计算"}
    op_title_map = {'add_subtract': "加减法", 'multiply_divide': "乘除法", 'all': "四则运算"}
    mode_title_map = {'mixed': "混合运算", 'sequential': "连续运算"}
    
    title_parts = [f"{max_number}以内"]
    if num_operands > 2:
        title_parts.append(mode_title_map.get(op_mode, ''))
    
    title_parts.append(op_title_map.get(operators, ''))
    title_parts.append(f"({num_operands}个运算数 {type_title_map.get(problem_type, '')}) ")
    title = " ".join(filter(None, title_parts))

    # --- PDF Creation ---
    pdf = PDF()
    pdf.set_title(title)
    pdf.add_page()
    
    if os.path.exists(FONT_PATH):
        pdf.set_font('NotoSansSC', '', 12)
    else:
        pdf.set_font('Arial', '', 12)

    problems = generate_problems(problem_type, max_number, num_operands, operators, num_problems, op_mode)
    
    # --- Layout Problems ---
    col_width = pdf.w / 2.5
    row_height = 10
    for i, problem in enumerate(problems):
        if i > 0 and i % 2 == 0:
            pdf.ln(row_height)
        pdf.cell(col_width, row_height, problem)

    # --- File Response ---
    filename = f"{uuid.uuid4()}.pdf"
    filepath = os.path.join(TMP_DIR, filename)
    
    try:
        pdf.output(filepath)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {e}")

    return FileResponse(filepath, media_type='application/pdf', filename=f"math_problems.pdf")
