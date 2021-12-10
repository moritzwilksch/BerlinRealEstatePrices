library(arrow)
library(dplyr)
library(ggplot2)
library(lme4)
library(lattice)

dfall = read_parquet("data/berlin_clean.parquet")

dfrent = dfall %>% filter(to_rent == TRUE & ! object_type %in% c("HOLIDAY_HOUSE_APARTMENT", "HOUSE"))
dfrent$object_type = droplevel(dfrent$object_type)

dfbuy = dfall %>% filter(to_rent == FALSE & ! object_type %in% c("HOLIDAY_HOUSE_APARTMENT", "SHARED_APARTMENT"))

## some properties with to_rent == TRUE actually have SALES prices!!!

dfrent$ppsqm = dfrent$price / dfrent$square_meters  # price per sqm
dfbuy$ppsqm = dfbuy$price / dfbuy$square_meters  # price per sqm

# "Rentals" that are actually for SALE
ggplot(data=dfrent %>% filter(ppsqm < 200), aes(x=ppsqm)) + geom_histogram() + theme_bw()
# most ppsqms are < 100 (sensible, although EUR100/sqm is VERY expensive, its not a SALE price)
# dfrent %>% filter(ppsqm > 100 & price > 10000) # to prevent wrong entries bc of close-to-zero sqm
dfrent[which(dfrent$ppsqm > 100 & dfrent$price > 10000),"to_rent"] = FALSE

# "Sales" that are actually RENTALS
ggplot(data=dfbuy %>% filter(ppsqm < 1000), aes(x=ppsqm)) + geom_histogram() + theme_bw()
# some ppsqms are < 250 (Way too cheap to be a sales price)
# dfbuy %>% filter(ppsqm < 250 & price < 10000) # to prevent wrong entries bc of close-to-zero sqm
dfbuy[which(dfbuy$ppsqm < 250 & dfbuy$price < 10000), "to_rent"] = TRUE
dfbuy[which(dfbuy$price < 10000), "to_rent"] = TRUE  # cheaper than 10k = rental


print("SALES that were classified as RENTALS")
dfrent %>% filter(to_rent == FALSE) %>% nrow()
print("Rentals that were classified as SALES")
sum(dfbuy %>% filter(to_rent == TRUE) %>% select("to_rent"))

all_new = rbind(dfrent, dfbuy)

dfrent = all_new %>% filter(to_rent == TRUE)
dfbuy = all_new %>% filter(to_rent == FALSE)

dfbuy = dfbuy %>% filter(price < 21474836)  # integer overflow in DB
x = dfbuy %>% filter(grepl("Vermittlung", title) | grepl("Prämie", title))  # remove calls for mediation of properties for premium

write_parquet(dfrent, "data/dfrent.parquet")
write_parquet(dfbuy, "data/dfbuy.parquet")