## import libraries
import pywikibot
from datetime import datetime, timedelta
import mwparserfromhell 
import re
import csv

##
def extract_comments_from_text(discussion_title, discussion_text):
    rows = []
    lines = discussion_text.split('\n')

    for line in lines:
        match = re.search(
            r"(?:\[\[User(?: talk)?:([^\]|]+).*?\]\]|User:([^\s]+))"
            r".*?(\d{1,2}:\d{2}),\s*"
            r"(?:(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})|"       # 1 Jan 2005
            r"([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})|"         # Jan 1, 2005
            r"(\d{4})\s+([A-Za-z]+)\s+(\d{1,2}))",         # 2005 Jan 1
            line
        )

        if match:
            username = match.group(1) or match.group(2)

            # Extract time
            time = match.group(3)

            # Detect which date format matched
            if match.group(4):  # Format: 1 Jan 2005
                day, month, year = match.group(4), match.group(5), match.group(6)
            elif match.group(7):  # Format: Jan 1, 2005
                day, month, year = match.group(8), match.group(7), match.group(9)
            elif match.group(10):  # Format: 2005 Jan 1
                day, month, year = match.group(12), match.group(11), match.group(10)
            else:
                continue  # Skip if somehow nothing matched

            date_str = f"{int(day)} {month} {year}"

            # Remove user signature from comment
            comment = re.sub(
                r"(?:\[\[User.*?\]\]|User:[^\s]+).*?\d{1,2}:\d{2}.*?(?:\d{4})",
                "",
                line
            ).strip()

            rows.append([
                discussion_title,
                username,
                date_str,
                time,
                comment
            ])

            print(f"🧾 User: {username} at {time}, {date_str}")
            print(f"💬 {comment[:100]}")

    return rows

## functions to parse through comments and recollect it




# connect to Wikipedia
site = pywikibot.Site("en", "wikipedia")

# set date range 
start_date = datetime(2005, 1, 1)
end_date = datetime(2007, 12, 31)
current_date = start_date

# list to collect all comment rows to later add to csv
all_rows = []

# get in date range
while current_date <= end_date:
    # create the date str where you do not have a 0 in front so 2005_January_1
    date_str = f"{current_date.year}_{current_date.strftime('%B')}_{current_date.day}"
    # get the page_title
    page_title = f"Wikipedia:Articles for deletion/Log/{date_str}"
    print(f"Processing: {page_title}")
    # create page object
    page = pywikibot.Page(site, page_title)
    # if page exists
    if page.exists():
        # get text
        text = page.text
        # get and parse text
        wikicode = mwparserfromhell.parse(text)
        # templates are all that start with {{}} this is exactly how alll the articles were 
        # {{Wikipedia:Votes for deletion/List of black metal genres}}
        templates = wikicode.filter_templates()
        #loop through templates
        for template in templates:
            # get the tamplate name
            template_name = template.name.strip()
            # if it starts with wikipedia deletion it assumes it's referencing a sub-discussion page
            # from 2005-2008 the deletion log created another page votes for deletion where the nominations were discussed
            if template_name.lower().startswith("wikipedia:votes for deletion/"):
                # to get the discussion page we delete the first part
                # while it does not make sense for url, it is better for parsing article title
                # it extracts "List of black metal genres"
                discussion_title = template_name[len("Wikipedia:Votes for deletion/"):].strip()
                print(f"Checking discussion page: {discussion_title}")
                # create the page
                discussion_page = pywikibot.Page(site, f"Wikipedia:Articles for deletion/{discussion_title}")
                # if page exists
                if discussion_page.exists():
                    # get redirects
                    if discussion_page.isRedirectPage():
                        discussion_page = discussion_page.getRedirectTarget()
                    # if found get the text
                    print(f"Discussion found: {discussion_page.title()}")
                    discussion_text = discussion_page.text
                    # use the function
                    comment_rows = extract_comments_from_text(discussion_title, discussion_text)
                    # append rows
                    all_rows.extend(comment_rows)
                else:
                    print(f"Discussion page does not exist: {discussion_page.title()}")
    else:
        print(f"The page '{page_title}' does not exist.")

    current_date += timedelta(days=1)

# write to CSV
with open("yearly_afd_comments_2005_2007.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["article", "user", "date", "timestamp", "comment"])
    writer.writerows(all_rows)

print("✅ CSV file 'afd_comments_2005_2days.csv' written successfully.")
