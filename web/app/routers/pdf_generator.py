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

    if num_operands > 2:
        allowed_ops = [op for op in allowed_ops if op in ['+', '-']]
        if not allowed_ops:
            return ["多运算数模式目前仅支持加减法。"]

    for _ in range(num_problems):
        problem_generated = False
        while not problem_generated:
            try:
                if problem_type == 'simple_calculation':
                    if num_operands < 2: continue
                    
                    current_value = random.randint(0, max_number)
                    problem_str = str(current_value)
                    
                    # For sequential mode, decide the operator before the loop
                    sequential_op = random.choice(allowed_ops) if op_mode == 'sequential' else None

                    for i in range(num_operands - 1):
                        op = sequential_op if sequential_op else random.choice(allowed_ops)
                        
                        if op == '+':
                            next_val = random.randint(0, max_number - current_value)
                            current_value += next_val
                            problem_str += f" + {next_val}"
                        elif op == '-':
                            next_val = random.randint(0, current_value)
                            current_value -= next_val
                            problem_str += f" - {next_val}"
                        # NOTE: Multi-operand multiply/divide is complex and excluded for now

                    problems.append(f"{problem_str} = ")
                    problem_generated = True

                elif problem_type == 'find_missing_number':
                    # This logic remains the same as it's complex enough already
                    # and op_mode is less relevant for missing number problems for now.
                    # (Code from previous step is unchanged here)
                    if num_operands == 2:
                        op = random.choice(allowed_ops)
                        if op == '+':
                            c = random.randint(1, max_number)
                            a = random.randint(0, c)
                            problems.append(f"{a} + ▢ = {c}")
                        elif op == '-':
                            a = random.randint(1, max_number)
                            c = random.randint(0, a)
                            problems.append(f"{a} - ▢ = {c}")
                        elif op == '*':
                            c = random.randint(0, max_number)
                            factors = [i for i in range(1, c + 1) if c % i == 0]
                            if not factors: continue
                            a = random.choice(factors)
                            problems.append(f"{a} × ▢ = {c}")
                        elif op == '/':
                            c = random.randint(1, max_number)
                            a = c * random.randint(1, max_number // c if c != 0 else max_number)
                            problems.append(f"{a} ÷ ▢ = {c}")
                        problem_generated = True
                    else: 
                        if num_operands == 3:
                            d = random.randint(1, max_number)
                            a = random.randint(0, d)
                            b = random.randint(0, d - a)
                            box_pos = random.randint(0, 2)
                            if box_pos == 0:
                                problems.append(f"▢ + {b} + {d-a-b} = {d}")
                            elif box_pos == 1:
                                problems.append(f"{a} + ▢ + {d-a-b} = {d}")
                            else:
                                problems.append(f"{a} + {b} + ▢ = {d}")
                            problem_generated = True
                        else:
                            problems.append("暂不支持超过3个运算数的未知数计算。")
                            problem_generated = True

            except (ValueError, ZeroDivisionError):
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
    if num_operands > 2 and operators == 'add_subtract':
        title_parts.append(mode_title_map.get(op_mode, ''))
    else:
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