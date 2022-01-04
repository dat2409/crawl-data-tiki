import requests
import json
import csv
import re

laptop_page_url = "https://tiki.vn/api/personalish/v1/blocks/listings?limit=48&include=advertisement&aggregations=2&trackity_id=091f9be1-b295-4812-c626-b095992eccdb&category=8322&page={}&urlKey=nha-sach-tiki"
product_url = "https://tiki.vn/api/v2/products/{}"

product_id_file = "./data/product-id2.txt"
product_data_file = "./data/product2.txt"
product_file = "./data/product2.csv"

headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"}


def crawl_product_id():
    product_list = []
    i = 1
    while (True):
        print("Crawl page: ", i)
        print(laptop_page_url.format(i))
        response = requests.get(laptop_page_url.format(i), headers=headers)

        if (response.status_code != 200):
            break

        products = json.loads(response.text)["data"]

        if (len(products) == 0):
            break

        for product in products:
            product_id = str(product["id"])
            print("Product ID: ", product_id)
            product_list.append(product_id)

        i += 1

    return product_list, i


def save_product_id(product_list=[]):
    file = open(product_id_file, "w+", encoding="utf-8-sig")
    str = "\n".join(product_list)
    file.write(str)
    file.close()
    print("Save file: ", product_id_file)


def crawl_product(product_list=[]):
    product_detail_list = []
    for product_id in product_list:
        response = requests.get(
            product_url.format(product_id), headers=headers)
        if (response.status_code == 200):
            product_detail_list.append(response.text)
            print("Crawl product: ", product_id, ": ", response.status_code)

    return product_detail_list


flatten_field = []


def adjust_product(product):
    e = json.loads(product)
    if not e.get("id", False):
        return None

    for field in flatten_field:
        if field in e:
            e[field] = json.dumps(
                e[field], ensure_ascii=False).replace('\n', '')

    return e


def save_raw_product(product_detail_list=[]):
    file = open(product_data_file, "w+", encoding="utf-8-sig")
    str = "".join(product_detail_list)
    file.write(str)
    file.close()
    print("Save file: ", product_data_file)


def load_raw_product():
    file = open(product_data_file, "r", encoding="utf-8-sig")
    return file.readlines()


def save_product_list(product_json_list):
    file = open(product_file, "w", encoding="utf-8-sig")
    csv_writer = csv.writer(file)

    count = 0
    for p in product_json_list:
        if p is not None:
            if count == 0:
                header = p.keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(p.values())

    file.close()
    print("Save file: ", product_file)


# crawl product id
product_list, page = crawl_product_id()

print("No. Page: ", page)
print("No. Product ID: ", len(product_list))

# save product id for backup
save_product_id(product_list)

# crawl detail for each product id
product_list = crawl_product(product_list)

# save product detail for backup
save_raw_product(product_list)

# product_list = load_raw_product()
# flatten detail before converting to csv
product_json_list = [adjust_product(p) for p in product_list]
# save product to csv
save_product_list(product_json_list)
