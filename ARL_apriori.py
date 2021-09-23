import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 500)
pd.set_option('display.expand_frame_repr', False)

from mlxtend.frequent_patterns import apriori, association_rules

"""
Aşağıda 3 farklı kullanıcının sepet bilgileri verilmiştir.
Bu sepet bilgilerine en uygun ürün önerisini yapınız.
Not: Ürün önerileri 1 tane ya da 1'den fazla olabilir.
Önemli not: Karar kurallarını 2010-2011 Germany
müşterileri üzerinden türetiniz.

▪ Kullanıcı 1 ürün id'si: 21987
▪ Kullanıcı 2 ürün id'si: 23235
▪ Kullanıcı 3 ürün id'si: 22747
"""

###Veri Ön İşleme İşlemlerini Gerçekleştiriniz
#Önemli not!
#2010-2011 verilerilerini seçiniz ve tüm veriyi ön işlemeden geçiriniz.

df_ = pd.read_excel("Ders Notları/online_retail_II.xlsx", sheet_name="Year 2010-2011")
df = df_.copy()
df.info()
df.head()

def outlier_thresholds(dataframe, variable):
    quartile1 = dataframe[variable].quantile(0.01)
    quartile3 = dataframe[variable].quantile(0.99)
    interquantile_range = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * interquantile_range
    low_limit = quartile1 - 1.5 * interquantile_range
    return low_limit, up_limit

def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    dataframe.loc[(dataframe[variable] < low_limit), variable] = low_limit
    dataframe.loc[(dataframe[variable] > up_limit), variable] = up_limit

def retail_data_prep(dataframe):
    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]
    dataframe = dataframe[dataframe["Quantity"] > 0]
    dataframe = dataframe[dataframe["Price"] > 0]
    replace_with_thresholds(dataframe, "Quantity")
    replace_with_thresholds(dataframe, "Price")
    return dataframe

df = retail_data_prep(df)
df.head(5)

df.loc[(df["StockCode"] == "POST")]
df.loc[(df["StockCode"] == "POST")]["Price"]
df[(df["StockCode"] == "POST")]["Price"].dropna().count() #post'suz data sayısı 1100 olduğunu bulduk.

df = df.loc[(df["StockCode"] != "POST")]

#Germany Müşterileri Üzerinden Birliktelik Kuralları Üretiniz

df_gr = df[df['Country'] == "Germany"]

def create_invoice_product_df(dataframe, id=False):
    if id:
        return dataframe.groupby(['Invoice', "StockCode"])['Quantity'].sum().unstack().fillna(0). \
            applymap(lambda x: 1 if x > 0 else 0)
    else:
        return dataframe.groupby(['Invoice', 'Description'])['Quantity'].sum().unstack().fillna(0). \
            applymap(lambda x: 1 if x > 0 else 0)

gr_inv_pro_df = create_invoice_product_df(df_gr)
gr_inv_pro_df.head()

def create_rules(dataframe, id=True, country="Germany"):
    dataframe = dataframe[dataframe['Country'] == country]
    dataframe = create_invoice_product_df(dataframe, id)
    frequent_itemsets = apriori(dataframe, min_support=0.01, use_colnames=True)
    rules = association_rules(frequent_itemsets, metric="support", min_threshold=0.01)
    return rules

rules_gr = create_rules(df, country="Germany")
rules_gr.head()

#ID'leri verilen ürünlerin isimleri nelerdir?
"""
Kullanıcı 1 ürün id'si: 21987
Kullanıcı 2 ürün id'si: 23235
Kullanıcı 3 ürün id'si: 22747
"""

def check_id(dataframe, stock_code):
    product_name = dataframe[dataframe["StockCode"] == stock_code][["Description"]].values[0].tolist()
    print(product_name)

check_id(df,21987) #PACK OF 6 SKULL PAPER CUPS
check_id(df,23235) #STORAGE TIN VINTAGE LEAF
check_id(df,22747) #POPPY'S PLAYHOUSE BATHROOM

#Sepetteki Kullanıcılar için Ürün Önerisi Yapınız

def arl_recommender(rules_df, product_id, rec_count=1):
    sorted_rules = rules_df.sort_values("lift", ascending=False)
    recommendation_list = []

    for i, product in sorted_rules["antecedents"].items():
        for j in list(product):
            if j == product_id:
                recommendation_list.append(list(sorted_rules.iloc[i]["consequents"]))

    recommendation_list = list({item for item_list in recommendation_list for item in item_list})

    return recommendation_list[:rec_count]

arl_recommender(rules_gr,21987,1)
#output : 21244
arl_recommender(rules_gr,23235,1)
#output : 20750
arl_recommender(rules_gr,22747,1)
#output : 22411

#Önerilen ürünlerin isimleri nelerdir?

check_id(df,21244) #BLUE POLKADOT PLATE
check_id(df,20750) #RED RETROSPOT MINI CASES
check_id(df,22411) #JUMBO SHOPPER VINTAGE RED PAISLEY