# 📚✨ Welcome to Wikipedia! 

Wikipedia develops at a rate of over 1.9 edits per second, with editors frequently disagreeing over article existence, as seen in Articles for Deletion (AfD) debates.
Our repo is centered about analyzing the way people debate in these spaces. We have prompt engineered LLM's to classify thousands of data collected:
- 🦙 Llama 3-70B.
- 🥝 Kimi K2.
  
Additionally we have incorporated the scripts to webscrape Wikipedia both at 2005-2007, and at 2023-2024.
The coarse labels we have decided to annotate are the following:

| Label              |  What it means                          |
| ------------------ |  -------------------------------------- |
| **fact**           |  *“The article is part of NYT.”*        |
| **value**          |  *“This is just my two cents.”*         |
| **policy**         |  *“WP:GNG says so.”*                    |
| **editorial/meta** |  *“I will add sources to the article."* |
| **other**          |  *“Off-topic, but thanks for coming.”*  |
