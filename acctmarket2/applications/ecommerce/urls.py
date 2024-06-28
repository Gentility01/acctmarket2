from django.urls import path

from acctmarket2.applications.ecommerce import views

app_name = "ecommerce"
urlpatterns = [
    path("add-product", views.AddProductView.as_view(), name="add_product"),
    path("add-category", views.AddCategoryView.as_view(), name="add_category"),
    path("list-category", views.ListCategoryView.as_view(), name="list_category"),
    path(
        "edit-category/<int:pk>/",
        views.EditCategoryView.as_view(),
        name="edit_category",
    ),
    path(
        "delete-category/<int:pk>/",
        views.DeleteCategoryView.as_view(),
        name="delete_category",
    ),
    path("list-product", views.ListProductView.as_view(), name="list_product"),
    path(
        "edit-product/<int:pk>/",
        views.EditProductView.as_view(),
        name="edit_product",
    ),
    path(
        "delete-product/<int:pk>/",
        views.DeleteProductView.as_view(),
        name="delete_product",
    ),
    path(
        "product-detail/<int:pk>/",
        views.ProductDetailView.as_view(),
        name="product_detail",
    ),
    path("add-tags", views.CreateProductTags.as_view(), name="add_tags"),
    path("list-tags", views.ListProductTags.as_view(), name="list_tags"),
    path("edit-tags/<int:pk>/", views.EditProductTags.as_view(), name="edit_tags"),
    path(
        "delete-tags/<int:pk>/",
        views.DeleteProductTags.as_view(),
        name="delete_tags",
    ),
    path(
        "create-product-image",
        views.ProductImagesCreateView.as_view(),
        name="create_product_image",
    ),
    path(
        "list-product-image",
        views.ListProductImages.as_view(),
        name="list_product_images",
    ),
    path(
        "update-product-image/<int:pk>/",
        views.UpdateProductImages.as_view(),
        name="update_product_image",
    ),
    path(
        "delete-product-image/<int:pk>/",
        views.DeleteProductImages.as_view(),
        name="delete_product_image",
    ),
    path(
        "product/<int:pk>/add-review/",
        views.AddReviewsView.as_view(),
        name="add_review",
    ),
    path("add-to-cart/", views.AddToCartView.as_view(), name="add_to_cart"),
    path("cart", views.CartListView.as_view(), name="cart_list"),
    path(
        "delete-from-cart",
        views.DeleteFromCartView.as_view(),
        name="delete_from_cart_list",
    ),
    path(
        "update-to-cart",
        views.UpdateCartView.as_view(),
        name="delete_from_cart_list",
    ),
    path("checkout", views.CheckoutView.as_view(), name="checkout"),
    path("proceed-payment", views.ProceedPayment.as_view(), name="proceed_payment"),
    path(
        "payment-complete",
        views.PaymentCompleteView.as_view(),
        name="payment_complete",
    ),
    path(
        "payment-failed",
        views.PaymentFailedView.as_view(),
        name="payment_failed",
    ),
    path(
        "wish-lists",
        views.WishlistListView.as_view(),
        name="wishlists",
    ),
    path(
        "add-to-wishlist",
        views.AddToWishlistView.as_view(),
        name="add_to_wishlist",
    ),
    path(
        "verify-payment/<str:reference>/",
        views.VerifyPaymentView.as_view(),
        name="verify_payment",
    ),
    path(
        "initiate-payment/<int:order_id>/",
        views.InitiatePaymentView.as_view(),
        name="initiate_payment",
    ),
    path(
        "purchased-product",
        views.PurchasedProductsView.as_view(),
        name="purchased_products",
    ),
    # path(
    #     "create-payment/<int:order_id>/",
    #       views.CreateNowPaymentViews.as_view(),
    #         name="create_nowpayment"
    # ),
    # path(
    #     "payment-callback/",
    #     views.PaymentCallbackView.as_view(), name="payment-callback"
    # ),
    path('create_nowpayment/<int:order_id>/', views.NowPaymentView.as_view(), name='create_nowpayment'),
    path('ipn/', views.ipn, name='ipn'),
]
