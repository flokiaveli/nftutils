# This script uses graphql requests to get assets from the Crypto.com api
# Then it goes through each asset on the page to look see when its auction ends (if it has one)
# You can change the hours variable to increase the window
# And if the search isn't going deep enough you can increase the pages value
# Make sure you "python -m pip install requests" to install the requests module

import requests
import datetime
import json

hours = 4
pages = 55

lion_assets_request = '''{"operationName":"GetAssets","variables":{"collectionId":"82421cf8e15df0edcaa200af752a344f","first":%s,"skip":%s,"cacheId":"getAssetsQuery-82421cf8e15df0edcaa200af752a344f","hasSecondaryListing":true,"sort":[{"order":"ASC","field":"price"}]},"query":"fragment UserData on User {
  uuid
  id
  username
  displayName
  isCreator
  avatar {
    url
    __typename
  }
  __typename
}

query GetAssets($audience: Audience, $brandId: ID, $categories: [ID!], $collectionId: ID, $creatorId: ID, $ownerId: ID, $first: Int!, $skip: Int!, $cacheId: ID, $hasSecondaryListing: Boolean, $where: AssetsSearch, $sort: [SingleFieldSort!], $isCurated: Boolean, $createdPublicView: Boolean) {
  public(cacheId: $cacheId) {
    assets(
      audience: $audience
      brandId: $brandId
      categories: $categories
      collectionId: $collectionId
      creatorId: $creatorId
      ownerId: $ownerId
      first: $first
      skip: $skip
      hasSecondaryListing: $hasSecondaryListing
      where: $where
      sort: $sort
      isCurated: $isCurated
      createdPublicView: $createdPublicView
    ) {
      id
      name
      copies
      copiesInCirculation
      creator {
        ...UserData
        __typename
      }
      main {
        url
        __typename
      }
      cover {
        url
        __typename
      }
      royaltiesRateDecimal
      primaryListingsCount
      secondaryListingsCount
      primarySalesCount
      totalSalesDecimal
      defaultListing {
        editionId
        priceDecimal
        mode
        auctionHasBids
        __typename
      }
      defaultAuctionListing {
        editionId
        priceDecimal
        mode
        auctionHasBids
        __typename
      }
      defaultSaleListing {
        editionId
        priceDecimal
        mode
        __typename
      }
      defaultPrimaryListing {
        editionId
        priceDecimal
        mode
        auctionHasBids
        primary
        __typename
      }
      defaultSecondaryListing {
        editionId
        priceDecimal
        mode
        auctionHasBids
        __typename
      }
      defaultSecondaryAuctionListing {
        editionId
        priceDecimal
        mode
        auctionHasBids
        __typename
      }
      defaultSecondarySaleListing {
        editionId
        priceDecimal
        mode
        __typename
      }
      likes
      views
      isCurated
      defaultEditionId
      isLiked
      __typename
    }
    __typename
  }
}
"}'''
lion_assets_request = lion_assets_request.splitlines()
lion_assets_request = " ".join(lion_assets_request)

detail_request = '''{"operationName":"getEditionByAssetId","variables":{"editionId":"%s","cacheId":"getEditionById-%s-undefined-undefined"},"query":"query getEditionByAssetId($editionId: ID, $assetId: ID, $editionIndex: Int, $cacheId: ID) {
  public(cacheId: $cacheId) {
    edition(id: $editionId, assetId: $assetId, editionIndex: $editionIndex) {
      id
      index
      listing {
        id
        price
        currency
        primary
        auctionCloseAt
        auctionHasBids
        auctionMinPriceDecimal
        priceDecimal
        mode
        isCancellable
        status
        __typename
      }
      primaryListing {
        id
        price
        currency
        primary
        auctionCloseAt
        auctionHasBids
        auctionMinPriceDecimal
        priceDecimal
        mode
        isCancellable
        status
        __typename
      }
      owner {
        uuid
        id
        username
        displayName
        avatar {
          url
          __typename
        }
        croWalletAddress
        isCreator
        __typename
      }
      ownership {
        primary
        __typename
      }
      chainMintStatus
      chainTransferStatus
      chainWithdrawStatus
      acceptedOffer {
        id
        user {
          id
          __typename
        }
        __typename
      }
      minOfferAmountDecimal
      mintTime
      __typename
    }
    __typename
  }
}
"}'''

detail_request = detail_request.splitlines()
detail_request = " ".join(detail_request)

if __name__ == "__main__":
    print("looking for lion auctions")
    url = 'https://crypto.com/nft-api/graphql'
    endpoint = datetime.datetime.utcnow()
    endpoint += datetime.timedelta(hours=hours)
    for i in range(pages):
        print("page", i)
        assets = requests.post(url, json = json.loads(lion_assets_request % (10, i * 10)))
        for asset in assets.json()['data']['public']['assets']:
            try:
                assetId = asset['id']
                name = asset['name']
                edition = asset['defaultListing']['editionId']
                detail = requests.post(url, json = json.loads(detail_request % (edition, edition)))
                price = float(detail.json()['data']['public']['edition']['listing']['priceDecimal'])
                closes_at = detail.json()['data']['public']['edition']['listing']['auctionCloseAt']
                if closes_at != None and datetime.datetime.strptime(closes_at, '%Y-%m-%dT%H:%M:%S.%fZ') < endpoint:
                    print(name, price, f'https://crypto.com/nft/collection/82421cf8e15df0edcaa200af752a344f?asset={assetId}&edition={edition}&detail-page=MARKETPLACE')
            except Exception as e:
                print(e)
