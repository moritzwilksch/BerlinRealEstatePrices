library(arrow)
library(dplyr)
library(ggplot2)


df = read_parquet("data/berlin.parquet")

df = df %>% filter(!object_type %in% c("NURSING_HOME", "RETIREMENT_HOME", "HOLIDAY_HOUSE_APARTMENT"))

################### EDA & Stats ###################

# Have to be divided by 100 as they are saved as int in the DB.
df$square_meters = df$square_meters / 100  # is now m^2
df$price = df$price / 100  # is now EUR

###### Explicit NA Values ######
colSums(is.na(df), 0)  # ~10k rooms missing

###### Implicit NA Values ######
# Private Offer
table(df$private_offer) # No NAs

# Square Meters
sum(df$square_meters == 0)  # ~5k with 0 sqm size
df$square_meters[df$square_meters == 0, "square_meters"] = NA  # make explicit

###### General EDA ######
### Created at (time of scrape)
min(df$created_at)  # 2021-04-25 13:04:57 EDT
max(df$created_at)  # 2021-10-27 13:57:33 EDT

### Location (dirty!)
# df$location  # ZIPCODE Berlin [Borough], [Address]

### Object Type
table(df$object_type) # Originally: only 3 nursing homes & 17 retirement homes
df$object_type = droplevels(df$object_type)


### Square Meters
# Very few, extreme outliers! (10,000,000 m^2)
ggplot(data=df %>% filter(square_meters < 1000), aes(x=square_meters)) + geom_histogram(bins=60)

quantile_cutoff = quantile(df$square_meters, 0.99, na.rm=T) # remove top 1% of outliers ONLY FOR PLOTTING 
ggplot(data=df %>% filter(square_meters < quantile_cutoff), aes(x=square_meters)) + geom_histogram(bins=60) + theme_bw()

# Also excludes some of the price outliers
ggplot(data=df %>% filter(square_meters < quantile_cutoff), aes(x=price)) + geom_histogram(bins=60) + theme_bw()

### Rent/Buy
table(df$to_rent)
dfrent = df %>% filter(to_rent==TRUE)
dfbuy = df %>% filter(to_rent==FALSE)
# Seems to be unreliable/with outliers for each category. Rent price up to 21,474,836 EUR

# make explicit
df[df$price == 0, "price"] = NA
df = df %>% filter(price >= 100)  # everything below 100EUR rent can be considered a data entry error or a "per sqm" price

### Price
ggplot(data=df, aes(x=price)) + geom_histogram(bins=60) + theme_bw()+ facet_wrap(~to_rent)
# rent distribution highly skewed (potentially includes properties to buy)

# rent_cutoff = quantile(dfrent$price, 0.99)
# buy_cutoff = quantile(dfbuy$price, 0.99)
# dfrent = dfrent %>% filter(price <= rent_cutoff)
# dfbuy = dfbuy %>% filter(price <= buy_cutoff)

# Rent prices
#ggplot(data=dfrent, aes(x=price)) + geom_histogram(bins=60) + theme_bw()  # some zeros

# Buy prices
#ggplot(data=dfbuy, aes(x=price)) + geom_histogram(bins=60) + theme_bw() # many zeros

### Private offer
table(df$private_offer, df$to_rent)  # fewer private offers than non-private

### Rooms
df[which(df$rooms %in% c("Zimmer k.A.", "k.A. Zimmer", "0")), "rooms"] = NA  # k.A. = keine Angabe = not given

df[which(df$rooms %in% c("Privatzimmer", "Einzelzimmer")), "rooms"] = "1"  # Privatzimmer <=> Private room, Einzelzimmer <=> Sinlge room
levels(df$rooms) = c(levels(df$rooms), "Shared", "Missing")
df[which(df$rooms == "Gemeinsames Zimmer"), "rooms"] = "Shared"  # Geimeinsames Zimmer <=> Shared room
df[which(is.na(df$rooms)), "rooms"] = "Missing"

# Exclude anything with more than 5 rooms or anything that only occurs once
tab = table(df$rooms)  # numerics (whole and decimal numbers) and text ("single room" [Einzelzimmer], "NA" [k.A.])
tab[tab > 1]  # only regard categories that occur multiple times
df = df %>% filter(rooms %in% names(tab[tab > 1] | is.na(df$rooms) | df$rooms == "Missing"))
df = df[as.numeric(as.character(df$rooms)) <= 5 | df$rooms %in% c("Shared", "Missing") | is.na(df$rooms), ]


# merge half-rooms into lower full rooms
df[which(df$rooms == 1.5), "rooms"] = "1"
df[which(df$rooms == 2.5), "rooms"] = "2"
df[which(df$rooms == 3.5), "rooms"] = "3"
df[which(df$rooms == 4.5), "rooms"] = "4"

df$rooms = droplevels(df$rooms)
ggplot(df, aes(x=rooms)) + geom_bar() + theme_bw()

### Square Meters
#sqm_cutoff = quantile(df$square_meters, 0.995, na.rm=T)
#df = df %>% filter(square_meters <= sqm_cutoff)
ggplot(df, aes(x=square_meters)) + geom_histogram() + theme_bw()


### ZIP Code
table(df$zip_code)  # some zips without data...
df$zip_code = droplevels(df$zip_code)

write_parquet(df, "data/berlin_clean.parquet")

