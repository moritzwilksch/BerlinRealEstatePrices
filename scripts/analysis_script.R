library(arrow)
library(dplyr)
library(ggplot2)
library(lme4)
library(lattice)

dfall = read_parquet("data/berlin_clean.parquet")

dfrent = dfall %>% filter(to_rent == TRUE & ! object_type %in% c("HOLIDAY_HOUSE_APARTMENT", "HOUSE"))
dfrent$object_type = droplevel(dfrent$object_type)

dfbuy = dfall %>% filter(to_rent == FALSE & ! object_type %in% c("HOLIDAY_HOUSE_APARTMENT", "SHARED_APARTMENT"))

rent_cutoff = quantile(dfrent$price, 0.98)
buy_cutoff = quantile(dfbuy$price, 0.99)
dfrent = dfrent %>% filter(price <= rent_cutoff)
dfbuy = dfbuy %>% filter(price <= buy_cutoff)

# Rent prices
ggplot(data=dfrent, aes(x=log(price))) + geom_histogram(bins=60) + theme_bw()  # some zeros

# Buy prices
ggplot(data=dfbuy, aes(x=price)) + geom_histogram(bins=60) + theme_bw() # many zeros

################### RENTAL UNITS ###################
################### EDA ###################
ggplot(data=dfrent, aes(x=square_meters, y=price, color=private_offer)) + geom_point(alpha=0.1) + theme_bw() + geom_smooth(method='lm')




model = lm(price ~ object_type + private_offer + rooms + square_meters, data=dfrent)
summary(model)

model2 = lmer(price ~ object_type + private_offer + rooms + square_meters + (1 | zip_code), data=dfrent)
summary(model2)

#%%
dfrent %>% group_by(object_type) %>% summarise(price=mean(price))


table(dfrent$object_type)

anova(model2, model)
dotplot(ranef(model2))
