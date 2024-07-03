import time
import openpyxl
import pandas as pd
from GetElements import GetElements

def clear_excel_file(filename, sheetName):
    """Clear a sheet from an Excel file."""
    wb = openpyxl.load_workbook(filename)
    sheet = wb[sheetName]
    sheet.delete_cols(1, 6)
    wb.save(filename)


def create_excel_file(dict):
    """Create a .xlsx file from a given dictionary."""

    filename = 'table_result.xlsx'
    df = pd.DataFrame.from_dict(dict, orient='index')
    clear_excel_file(filename, 'News')
    try:
        writer = pd.ExcelWriter(filename)
        df.to_excel(writer, sheet_name='News', index=False)
        writer._save()

    except PermissionError:
        pass

def main(browser):
    # Parameters
    WEBSITE = "https://apnews.com/"
    TEXT_TO_SEARCH = "Robotics"
    MONTHS = 1

    #TEXT_TO_SEARCH = input("What do you want to search?")
    #try:
    #    MONTHS = int(input("Enter the number of months for which you need to receive news:"))
    #except ValueError:
    #    print("Enter an integer!")

    browser.start_browser(WEBSITE, 0)
    browser.search(TEXT_TO_SEARCH)
    browser.filter()
    news = browser.get_data(MONTHS)

    create_excel_file(news)

if __name__ == "__main__":

    # Dictionary with CSS parameters from the website https://apnews.com/
    websiteDict = {
        'searchButton': "SearchOverlay-search-button",
        'textInput': "SearchOverlay-search-input",
        'selectionNewest': {'element': "select.Select-input",
                            'value': "3"},
        'selectionFilter': {'element': "div.SearchFilter-heading",
                            'checkbox': "label.CheckboxInput-label"},
        'results': "div.SearchResultsModule-results div.PageList-items-item",
        'resultElements': {'name': "div.PagePromo-title span.PagePromoContentIcons-text",
                           'date': "span.Timestamp-template",
                           'desc': "div.PagePromo-description span.PagePromoContentIcons-text",
                           'img': "div.PagePromo-media img"},
        'nextPage': "div.Pagination-nextPage a",
        'popUP': "div.fancybox-outer a"
    }

    browser = GetElements(websiteDict)
    main(browser)
    time.sleep(3)
    browser.close_browser()