import sqlite3
import json

db_path = "/Users/seomanager/Project/trade/polymarket_products.db"
output_path = "/Users/seomanager/Project/polygit/README.md"

def cat_sort_key(cat):
    if cat[1] == 'Trading Bots & Terminals':
        return 0
    else:
        return 1

def generate_awesome_list():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Get all categories
    cur.execute("SELECT id, name, slug, description FROM categories ORDER BY name ASC")
    categories = cur.fetchall()
    
    # Sort categories: Trading Bot first, Trading Terminal second, then others alphabetically
    categories.sort(key=lambda x: (cat_sort_key(x), x[1]))
    
    md_content = """# 🌟 Awesome Polymarket Trading Bots, Analysis Tools And More

> **A beautifully curated, categorized list of the best tools, bots, and resources for the Polymarket prediction market ecosystem.**

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

⭐ **If you find this directory helpful, please give it a Star! This list is updated frequently with the newest tools and market analytics.** ⭐

This list is generated directly from our verified database, featuring comprehensive insights, user ratings, and detailed summaries of the products shaping the future of information markets.

---

## 📑 Table of Contents

"""
    
    # Generate Table of Contents
    for cat in categories:
        cat_id, cat_name, cat_slug, cat_desc = cat
        md_content += f"- [{cat_name}](#{cat_slug})\n"
        
    md_content += "\n---\n\n"
    
    # Generate content for each category
    for cat in categories:
        cat_id, cat_name, cat_slug, cat_desc = cat
        
        md_content += f"## {cat_name}\n"
        md_content += f"<a name=\"{cat_slug}\"></a>\n\n"
        
        if cat_desc:
            md_content += f"*{cat_desc}*\n\n"
            
        # Get products for this category
        cur.execute('''
            SELECT name, website_url, summary, shortinfo, rating, rating_count, slug, rank
            FROM products 
            WHERE category_id = ?
            ORDER BY 
                CASE WHEN rank IS NOT NULL AND rank != '' THEN 0 ELSE 1 END ASC,
                CASE WHEN CAST(rank AS INTEGER) = 0 THEN 9999 ELSE CAST(rank AS INTEGER) END ASC,
                lastmod DESC,
                rating DESC, 
                rating_count DESC, 
                name ASC
        ''', (cat_id,))
        
        products = cur.fetchall()
        
        if not products:
            md_content += "_No products currently in this category._\n\n"
            continue
            
        for p in products:
            p_name, p_url, p_summary, p_shortinfo, p_rating, p_count, p_slug, p_rank = p
            
            # Format rating
            rating_text = ""
            if p_rating is not None and p_count is not None and p_count > 0:
                stars_count = int(round(p_rating))
                stars = "★" * stars_count + "☆" * (5 - stars_count)
                rating_text = f" | {stars} **{p_rating:.1f}/5** ({p_count} ratings)"
            
            # Check if slug should go to polymart.app
            polymart_slugs = {
                'chance', 'kreo', 'polycop', 'polygun', 'polymarket-analytics',
                'polymarket-cli', 'predictfolio', 'wagerup'
            }
            
            base_slug = p_slug
            if p_slug in ('polycop-analytics', 'polygun-analytics'):
                base_slug = p_slug.replace('-analytics', '')

            if base_slug in polymart_slugs:
                info_link = f" [ℹ️](https://polymart.app/{base_slug})"
            else:
                info_link = f" [ℹ️](https://polyzone.app/{p_slug}/)"
            
            md_content += f"### [{p_name}]({p_url}){rating_text}{info_link}\n\n"
            
            desc = p_summary if p_summary else p_shortinfo
            if desc:
                md_content += f"> {desc}\n\n"
                    
            # Add some spacing
            md_content += "---\n\n"
            
    # Add footer
    md_content += """
## 🤝 Contributing
Contributions are welcome! If you'd like to add new amazing tools or update existing information, please submit a Pull Request on GitHub or contact me directly on Telegram at [@SolanaLevelUp](https://t.me/SolanaLevelUp).

## 📝 License
[![CC0](https://mirrors.creativecommons.org/presskit/buttons/88x31/svg/cc-zero.svg)](https://creativecommons.org/publicdomain/zero/1.0/)

> *This data is curated and shared with the permission of [Polyzone.app](https://polyzone.app).*
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    print(f"Generated {output_path} successfully!")

if __name__ == "__main__":
    generate_awesome_list()
