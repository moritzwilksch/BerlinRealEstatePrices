library(arrow)
library(dplyr)
library(ggplot2)
library(lme4)
library(lattice)

dfrent = read_parquet("data/dfrent.parquet")
dfbuy = read_parquet("data/dfbuy.parquet")

#rent_cutoff = quantile(dfrent$price, 0.99)
#buy_cutoff = quantile(dfbuy$price, 0.99)
#dfrent = dfrent %>% filter(price <= rent_cutoff)
#dfbuy = dfbuy %>% filter(price <= buy_cutoff)

# square_meters outliers
dfrent_cutoff = quantile(dfrent$square_meters, 0.999, na.rm=TRUE)
dfbuy_cutoff = quantile(dfbuy$square_meters, 0.999, na.rm = TRUE)

nrow(dfrent %>% filter(square_meters > dfrent_cutoff))  # removes 21 outliers
nrow(dfbuy %>% filter(square_meters > dfbuy_cutoff))  # removes 32 outliers

dfrent = dfrent %>% filter(square_meters <= dfrent_cutoff)
dfbuy = dfbuy %>% filter(square_meters <= dfbuy_cutoff & rooms != "Shared")

dfbuy$rooms = droplevels(dfbuy$rooms)

####################################################
################### SALES UNITS ####################
####################################################

################### EDA ###################

# price by sqm
ggplot(data=dfbuy, aes(x=square_meters, y=price, color=private_offer)) + geom_point(alpha=0.1) + theme_bw() + geom_smooth(method='lm')

# rooms * sqm interaction
# same direction, but different slopes per n_rooms
ggplot(data=dfbuy, aes(x=square_meters, y=price)) + geom_point(alpha=0.5) + geom_smooth(method="lm") + facet_grid(~ rooms)


################### Modelling - Non-hierarchical ###################
# all mean effects
model0 = lm(log(price) ~ object_type + private_offer + rooms + square_meters, data=dfbuy)
summary(model0)
# plot(model0)

#high_dist = c(90, 12546)
#problematic = c(12453, 2475, 9284, 30622, 18394, 22205, 17716, 5827, 30619)
problematic = c(747, 1048, 22411, 90, 12780)
leverage_removed = dfbuy[-problematic, ]
problematic = c(3397, 20318, 10983, 7696)
leverage_removed = leverage_removed[-problematic, ]
problematic = c(17272, 27480, 2240)
leverage_removed = leverage_removed[-problematic, ]


model0 = lm(log(price) ~ object_type + private_offer + rooms + square_meters, data=leverage_removed)
summary(model0)
# plot(model0)

# room x sqm interaction
model1 = lm(log(price) ~ object_type + private_offer + rooms * square_meters, data=leverage_removed)
summary(model1)
# plot(model1)

anova(model1, model0)

################### Modelling - Hierarchical ###################
model2 = lmer(log(price) ~ object_type + private_offer + rooms * square_meters + (1 | zip_code), data=leverage_removed)
summary(model2)
# xtable(coef(summary(model2)))

anova(model2, model1)
dotplot(ranef(model2))


## Export Section
ranef(model2)$zip_code
x = ranef(model2, condVar=TRUE)$zip_code
xdf = data.frame(pointest=ranef(model2, condVar=TRUE)$zip_code, err=as.vector(sqrt(attr(x, "postVar"))))
xdf$pointestimate = xdf$X.Intercept.
xdf$zip = rownames(xdf)
xdf$X.Intercept. = NULL
write_parquet(xdf, "data/intermediaries/ranef_by_zipcode_sales.parquet")
#######################
