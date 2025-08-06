from collections import defaultdict
from bs4 import BeautifulSoup


def parsing_res_to_prompt(parsing_res_list):
    categorized_blocks = defaultdict(list)
    table_count = 0

    # Sort by reading order
    parsing_res_list = sorted(parsing_res_list, key=lambda x: x.get("index", 0))

    for block in parsing_res_list:
        label = block.get("block_label", "unknown")
        content = block.get("block_content", "").strip()

        if not content or len(content) < 5:
            continue  # skip short/noisy blocks

        if label == "table":
            table_count += 1
            table_2d = table_parsing(block.get("block_content", "unknown"))  # your pre-parsed 2D table
            if table_2d:
                header = table_2d[0]
                rows = table_2d[1:]
                md_table = ["| " + " | ".join(header) + " |",
                            "| " + " | ".join(['---'] * len(header)) + " |"]
                for row in rows:
                    md_table.append("| " + " | ".join(row) + " |")
                categorized_blocks["table"].append((f"Table {table_count}", "\n".join(md_table)))
        else:
            categorized_blocks[label].append(content)

    # Build prompt
    # prompt = f"You are a medical data extraction assistant. Your task is to extract all **clinical health metrics** or the **body function metrics** from the provided text **exactly as they appear** in the document.\n"
    # prompt += f"""### Extraction Instructions:
    #             - Look for metrics in **tabular format.** 
    #             - If you find any other medical term or metric that is not mentioned in the list of keywords, please mention it.
    #             - Extract all metrics that match or are similar to the following keywords:
    #                 {'\n'.join(keywords)}

    #             - Only extract information that is **explicitly present** in the text.
    #             - If a metric is **not found**, leave its value as `null` or an empty string. Do **not infer** or guess any values.
    #             """
    
    prompt = "\n--- Page Content Start ---\n\n"

    # Include titles first if present
    if categorized_blocks.get("title"):
        prompt += "Titles:\n" + "\n".join(categorized_blocks["title"]) + "\n\n"

    # Include regular text blocks
    if categorized_blocks.get("text"):
        prompt += "Text Blocks:\n" + "\n\n".join(categorized_blocks["text"]) + "\n\n"

    # Include tables
    if categorized_blocks.get("table"):
        prompt += "Tables:\n"
        for table_name, table_content in categorized_blocks["table"]:
            prompt += f"{table_name}:\n{table_content}\n\n"
        

    # Optionally include other labels
    for label, blocks in categorized_blocks.items():
        if label in {"title", "text", "table"}:
            continue
        section_name = label.replace("_", " ").title()
        prompt += f"{section_name} Blocks:\n" + "\n\n".join(blocks) + "\n\n"

    prompt += "--- Page Content End ---\n\n"

    
    return prompt
            

def table_parsing(html_string):
    html =   html_string
    soup = BeautifulSoup(html, 'html.parser')

    table = soup.find('table')
    rows = table.find_all('tr')

    data = []
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        if cols:
            data.append(cols)
    
    return data