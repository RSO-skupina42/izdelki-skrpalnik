# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import psycopg2


class MyprojectPipeline:
    def process_item(self, item, spider):
        return item


class PostgresDemoPipeline(object):
    def __init__(self):
        hostname = 'mouse.db.elephantsql.com'
        username = 'futdszan'
        password = 'eU6ph2tNtADEn3sNiLmGKpddr6ZuIIIM'
        database = 'futdszan'

        ## Create/Connect to database
        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)

        ## Create cursor, used to execute commands
        self.cur = self.connection.cursor()

        ## Create quotes table if none exists
        self.cur.execute("DROP TABLE stores")
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS stores(
            id serial PRIMARY KEY, 
            store_elem_id text, 
            store_name text,
            title text,
            description text,
            category text,
            price text,
            item_size text,
            sales_unit text,
            url text
        )
        """)
        self.temporary_db = []
        self.demo_fill_data_tus()

    def demo_fill_data_tus(self):
        # fill some dummy tus product data
        demo_tus_data = [
            ("8025332000018",
             "tus",
             "Češnjev paradižnik v grozdih",
             "Češnjev paradižnik v grozdih, pakirano, 500 g",
             "Sadje in zelenjava",
             "g",
             "500",
             "1.79",
             "https://www.tus.si/izdelki/cesnjev-paradiznik-v-grozdih-pakirano-500-g/"),
            ("3831001818632",
             "tus",
             "Testenine, polži, amorosi št. 32",
             "Testenine, polži, amorosi št. 32, 500 g",
             "Osnovna živila",
             "g",
             "500",
             "1.29",
             "https://www.tus.si/izdelki/testenine-polzi-amorosi-st-32-500-g/"),
            ("3838800024967",
             "tus",
             "Alpsko mleko, pol posneto, 1.5 % m.m.",
             "Alpsko mleko, pol posneto, 1.5 % m.m., 1 l",
             "category",
             "l",
             "1",
             "1.09",
             "https://www.tus.si/izdelki/alpsko-mleko-pol-posneto-1-5-m-m-1-l/"),
        ]
        self.temporary_db += demo_tus_data
        # args_str = b','.join(self.cur.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s,%s)", x) for x in demo_tus_data)
        # # print(args_str)
        # self.cur.execute(b"INSERT INTO stores (store_elem_id, store_name, title, description, category, sales_unit, item_size, price, url) VALUES " + args_str)
        # self.connection.commit()

    def process_item(self, item, spider):
        self.temporary_db.append((
            item["store_elem_id"],
            item["store_name"],
            item["title"],
            item["description"],
            item["category"],
            item["sales_unit"],
            item["item_size"],
            item["price"],
            item["url"],
        ))
        return item

    def close_spider(self, spider):
        args_str = b','.join(self.cur.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s,%s)", x) for x in self.temporary_db)
        # print(args_str)
        self.cur.execute(b"INSERT INTO stores (store_elem_id, store_name, title, description, category, sales_unit, item_size, price, url) VALUES " + args_str)
        self.connection.commit()
        ## Close cursor & connection to database
        self.cur.close()
        self.connection.close()
