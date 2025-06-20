import csv
import sys


def read_csv_to_list(file_path):
    """
    Reads a CSV file and returns a list of rows (each row is a list of values).
    """
    with open(file_path, 'r', newline='') as f:
        reader = csv.reader(f)
        data = [row for row in reader]
    return data


if __name__ == '__main__':
    threshold = float(sys.argv[1])
    elements = read_csv_to_list('bigtest_wod_2')
    print("len: ", len(elements))


    correct, incorrect, too_high_threshold, tn, fn = 0, 0, 0, 0, 0
    mismatch = 0
    for el in elements:
        if el[0]  in el[1] and float(el[3]) >= threshold:
            correct+=1
        elif el[0] not in el[1] and float(el[3]) > threshold:
            incorrect+=1
            print(el[0], el[1], el[3])
        elif el[0] in el[1] and float(el[3]) < threshold:
            too_high_threshold += 1
        elif "/b/" in el[1]:
            tn += 1
        elif "/a/" in el[1]:
            fn += 1



    print("Correct detections (TP): ", correct)
    print("Incorrect detections (FP): ", incorrect)
    print("threshold to high (also FN): ", too_high_threshold)
    print("TN", tn)
    print("other FN", fn)
    print("mismatch", mismatch)
