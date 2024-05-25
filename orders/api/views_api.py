import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from products.models import Product
from .serializers import AddToOrderItemSerializer


class AddToOrderItem(APIView):

    def post(self, request):
        serializer = AddToOrderItemSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']

            # Retrieve the existing dictionary from the cookie
            product_counts_json = request.COOKIES.get('product_counts')
            if product_counts_json:
                product_counts = json.loads(product_counts_json)
            else:
                product_counts = {}

            if product_id and product_id > 0:
                # Product capacity
                product = Product.objects.filter(id=product_id).first()
                if not product:
                    return Response({'response': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

                product_stock = product.stock

                # Count of added products
                added_product_count = product_counts.get(str(product_id), 0)
                if product_stock > added_product_count:
                    # Increment the count for the product ID
                    product_counts[str(product_id)] = product_counts.get(str(product_id), 0) + 1

                    # Serialize the updated dictionary to a JSON string
                    product_counts_json = json.dumps(product_counts)

                    # Prepare the response message and include product details
                    message = f"{product.name} added to cart"
                    response_data = {'response': message}

                    # Add product details to the response
                    for prod_id, count in product_counts.items():
                        prod = Product.objects.get(id=prod_id)
                        response_data[prod.name] = count

                    # Set the updated dictionary in the cookie
                    response = Response(response_data)
                    response.set_cookie('product_counts', product_counts_json)
                    return response
                else:
                    return Response({'response': 'Not enough products'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'response': 'Invalid product ID'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
