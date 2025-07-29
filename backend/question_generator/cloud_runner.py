from question_generator.generator import generate_questions
import sys

def main():
    summary = sys.argv[1] 
    result = generate_questions(summary)
    print("Generated Questions:\n", result)

if __name__ == "__main__":
    main()
