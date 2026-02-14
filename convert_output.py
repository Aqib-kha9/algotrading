
try:
    with open('comparison_result.txt', 'r', encoding='utf-16') as f:
        content = f.read()
    
    with open('summary.txt', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Converted to UTF-8")
except Exception as e:
    print(e)
