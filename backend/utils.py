import json

def extract_answers(answers):
    """Extract and format answers from assignment data"""
    result = {}
    for item in answers:
        key = item.get("dataKey")
        ans = item.get("answer")

        if isinstance(ans, list):
            if all(isinstance(i, dict) and 'value' in i and 'label' in i for i in ans):
                gabungan = [f"{i['value']}. {i['label']}" for i in ans]
                result[key] = ", ".join(gabungan)
            else:
                result[key] = ", ".join(str(i) for i in ans)
        elif isinstance(ans, dict):
            value = ans.get('value', '')
            label = ans.get('label', '')
            result[key] = f"{value}. {label}"
        else:
            result[key] = str(ans) if ans is not None else ""
    return result


def parse_assignment_status(data_json):
    """Parse assignment status from history"""
    hasil = []
    data_list = data_json.get("data", [])

    if not data_list:
        hasil.append({
            "No": 0,
            "assignment_id": None,
            "date": None,
            "status_assignment": "Open"
        })
    else:
        for i, item in enumerate(data_list, start=1):
            hasil.append({
                "No": i,
                "assignment_id": item.get("assignment_id"),
                "date": item.get("date_created"),
                "status_assignment": item.get("status_alias")
            })
    
    return hasil


def get_status_keberadaan(api_response: dict) -> str:
    """Get status keberadaan (data6) from API response"""
    try:
        return api_response['data']['data6']
    except (TypeError, KeyError):
        return None
