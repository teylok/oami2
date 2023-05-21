import subprocess

def clear_database(source):
    subprocess.run(["./oa-cache", "clear-database", source])

def detect_duplicates(doi_list):
    doi_string = ' '.join(doi_list)
    subprocess.run(["./oami_pmc_doi_detect_duplicates"], input=doi_string.encode(), text=True)

def main():
    source = "pmc_doi"
    dois = ["10.1371/journal.pone.0050188",
            "10.1371/journal.pone.0047867",
            "10.1186/1472-6785-10-9",
            "10.1371/journal.pone.0061541",
            "10.1371/journal.pone.0048222",
            "10.1371/journal.pone.0038803",
            "10.1371/journal.pone.0062199"]

    clear_database(source)
    detect_duplicates(dois)

if __name__ == "__main__":
    main()
