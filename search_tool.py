from ddgs import DDGS

def search_competitors(query, max_results=5):
    """
    指定されたクエリで競合サービスを検索し、結果をリストで返します。
    """
    results = []
    with DDGS() as ddgs:
        # textメソッドでWeb検索を実行
        search_results = ddgs.text(query, 
                                   region='jp-jp', 
                                   safesearch='off', 
                                   timelimit='y', 
                                   max_results=max_results)
        
        for r in search_results:
            results.append({
                'title': r['title'],
                'url': r['href'],
                'snippet': r['body']
            })
    return results

if __name__ == "__main__":
    # テスト実行
    test_query = "タスク管理アプリ 競合 類似サービス"
    print(f"「{test_query}」を検索中...")
    
    findings = search_competitors(test_query)
    
    for i, result in enumerate(findings, 1):
        print(f"\n[{i}] {result['title']}")
        print(f"URL: {result['url']}")
        print(f"概要: {result['snippet'][:100]}...") 