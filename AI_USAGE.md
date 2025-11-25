## AI Usage

- Assisted creating initial file structure setup "I need to setup my initial file structure". The suggestion was used to setup the initial pyproject.toml.

- Assisted in creating test prompts for ALU, FPU, MDU files. Such prompts included "I want to test the following file to see if it's working as intended, give me a skeleton test file in python"

- Assisted in formating **README.md**, prompts included "This is what my program does: _, can you format this in a .md format similar to what I already have here: _"

- **gen_ai_report.py** was AI generated to count all of the AI assisted sections of my code. Prompt went as follows: "I just now created the ai_report.json and AI_USAGE.md. How do I set those two up?"

AI-assisted regions of code were tagged with **AI-BEGIN** / **AI-END**.
An **AI_USAGE.md** summarizes tools, prompts, and scope; **ai_report.json** records counts.

(Per the course policy: tests compute references with host numerics; implementation modules do not use host numeric ops for arithmetic or shifting.)