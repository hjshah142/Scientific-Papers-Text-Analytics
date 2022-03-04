from LatexFileSummarizer import *
from LatexFileSummarizer.text_summarizer import TextSummarizer
from LatexFileSummarizer.latex_files_merger import LatexFilesMerger
from LatexFileSummarizer.latex_text_parser import LatexTextParser

latex_dir_name = r"C:\Users\lenovo\Downloads\[KI] Hybrid Loss for Algorithm Selection_ Regression and Ranking Loss"
main_file_path = r"C:\Users\lenovo\Downloads\[KI] Hybrid Loss for Algorithm Selection_ Regression and Ranking Loss\main.tex"
merged_file_path = "latex_sample_merged.tex"


def merge_latex_files(latex_dir_name, main_latex_file_path, merged_file_path):
    latex_file_merger = LatexFilesMerger(latex_dir_name, main_latex_file_path)
    merged_text_content = latex_file_merger.latex_files_merger()
    try:
        with open(merged_file_path, "w") as f:
            print("Merged File", merged_file_path, "created !!!")
            f.write(merged_text_content)
    except FileNotFoundError:
        print("The directory does not exist/accecible")

    return merged_text_content


merged_text_content = merge_latex_files(latex_dir_name, main_file_path, merged_file_path)
latex_parser = LatexTextParser(merged_file_path)
section_content, abstract, section_names = latex_parser.latex_text_parser()
print(section_names)

sections_summry_dict = {}
for sections in section_content:
    print(sections)
    text_summary_dict = TextSummarizer.text_summarizer(section_content[sections])
    sections_summry_dict[sections] = text_summary_dict
