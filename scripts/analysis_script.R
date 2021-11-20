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
dfbuy = dfbuy %>% filter(square_meters <= dfbuy_cutoff)

# Rent prices
ggplot(data=dfrent, aes(x=price)) + geom_histogram(bins=60) + theme_bw()  # some zeros

# Buy prices
ggplot(data=dfbuy, aes(x=price)) + geom_histogram(bins=60) + theme_bw() # many zeros

################### RENTAL UNITS ###################
################### EDA ###################

# price by sqm
ggplot(data=dfrent, aes(x=square_meters, y=price, color=private_offer)) + geom_point(alpha=0.1) + theme_bw() + geom_smooth(method='lm')

# rooms * sqm interaction
# same direction, but different slopes per n_rooms
ggplot(data=dfrent, aes(x=square_meters, y=price)) + geom_point(alpha=0.5) + geom_smooth(method="lm") + facet_grid(~ rooms)




################### Modelling - Non-hierarchical ###################
model0 = lm(ppsqm ~ object_type + private_offer + rooms + square_meters, data=dfrent)
summary(model0)

plot(model0)

compdf = data.frame(ytrue=dfrent$price, yhat=exp(predict(model0, dfrent)))
ggplot(data=compdf, aes(x=ytrue, y=yhat)) + geom_point(alpha=0.1)



model1 = lm(price ~ object_type + private_offer + rooms * square_meters, data=dfrent)
summary(model1)











################### Modelling - Hierarchical ###################


model2 = lmer(price ~ object_type + private_offer + rooms + square_meters + (1 | zip_code), data=dfrent)
summary(model2)

#%%
dfrent %>% group_by(object_type) %>% summarise(price=mean(price))


table(dfrent$object_type)

anova(model2, model)
dotplot(ranef(model2))











######## EXPERIMENT: PREDICTING PPSQM ###########
dfrent = dfrent %>% filter(ppsqm <= quantile(dfrent$ppsqm, 0.99))
ggplot(data=dfrent, aes(x=ppsqm)) + geom_histogram()

mse = function(model, data, ytrue, predict_ppsqm){
 preds = predict(model, data)
 if (predict_ppsqm == TRUE){
   preds = preds * data$square_meters
 }
 return(mean((preds - ytrue)^2))
}

exp_model0 = lm(ppsqm ~ object_type + private_offer + rooms + square_meters, data=dfrent)
print(mse(exp_model0, dfrent, dfrent$ppsqm, predict_ppsqm=TRUE))

exp_model1 = lm(price ~ object_type + private_offer + rooms + square_meters, data=dfrent)
print(mse(exp_model1, dfrent, dfrent$price, predict_ppsqm=FALSE))
############## END OF EXPERIMENT ################
