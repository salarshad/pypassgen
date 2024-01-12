from stats import calculate_stats
import sys

def read_file(filename):
    try:
        with open(filename, 'r') as fp:
            for line in fp:
                word = line.strip()
                if word.isalpha():
                    yield word.lower()
                else:
                    continue

    except FileNotFoundError:
        print(f"** file {filename} not found")
        return False

def process_file(filename):
    stats = calculate_stats(read_file(filename))
    print(stats)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("USAGE: python gen_stats.py /usr/dict/words")
        sys.exit(1)
    process_file(sys.argv[1])
    