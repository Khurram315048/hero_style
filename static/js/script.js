
function addToCartWithQuantity(btn){
  let id=btn.dataset.id;
  let title=btn.dataset.title;
  let basePrice=parseInt(btn.dataset.price);
  let quantity=parseInt(document.getElementById('quantity').value) || 1;  
  let price=basePrice;  
  let image=btn.dataset.img;
  
  if(image && !image.startsWith('/') && !image.startsWith('http')){
    image='/static/' + image;
  }

  let cart=JSON.parse(localStorage.getItem("cart")) || [];
  let existing=cart.find(item => item.id == id);

  if(existing){
    existing.quantity += quantity;  
  } 
  else{
    cart.push({id,title,price,image,quantity});  
  }

  localStorage.setItem("cart", JSON.stringify(cart));
  updateCartCount();
  alert('Added to cart!');  
}

  function updateCartCount(){
    let cart=JSON.parse(localStorage.getItem("cart")) || [];
    let total=cart.reduce((sum, item) => sum + item.quantity, 0);
    let counter=document.getElementById("cart-count");
    if (counter) counter.innerText = total;
  }

  function loadCartPage(){
    let cart=JSON.parse(localStorage.getItem("cart")) || [];
    let cartBody=document.getElementById("cart-body");
    let total=0;

    if(!cartBody){
      return;
    }

    cartBody.innerHTML="";

    if(cart.length===0){
      cartBody.innerHTML= `<tr><td colspan="5">Your cart is empty.</td></tr>`;
      document.getElementById("grand-total").innerText="PKR 0";
      return;
    }

    cart.forEach((item, index) => {
      let itemTotal = item.price * item.quantity;
      total += itemTotal;

      cartBody.innerHTML += `
        <tr>
          <td class="cart-product">
            <img src="${item.image}" class="cart-img" width="80" height="80">
            <span>${item.title}</span>
          </td>
          <td>PKR ${item.price}</td>
          <td>
            <div class="qty-box">
              <button onclick="changeQty(${index}, -1)">-</button>
              <span>${item.quantity}</span>
              <button onclick="changeQty(${index}, 1)">+</button>
            </div>
          </td>
          <td><strong>PKR ${itemTotal}</strong></td>
          <td><button class="remove-btn" onclick="removeItem(${index})">Remove</button></td>
        </tr>
      `;
    });

    document.getElementById("grand-total").innerText = "PKR " + total;
  }

  function changeQty(index, delta){
    let cart=JSON.parse(localStorage.getItem("cart")) || [];
    cart[index].quantity += delta;
    if (cart[index].quantity <= 0) cart.splice(index, 1);
    localStorage.setItem("cart", JSON.stringify(cart));
    loadCartPage();
    updateCartCount();
  }

  function removeItem(index){
    let cart = JSON.parse(localStorage.getItem("cart")) || [];
    cart.splice(index, 1);
    localStorage.setItem("cart", JSON.stringify(cart));
    loadCartPage();
    updateCartCount();
  }


  document.addEventListener("DOMContentLoaded",() => {
    updateCartCount();
    loadCartPage();
  });



function submitCheckout(e){
  e.preventDefault();

  let cart=JSON.parse(localStorage.getItem("cart")) || [];

  if (cart.length === 0) {
    alert("Your cart is empty.");
    return;
  }

  document.getElementById("cart-data-input").value = JSON.stringify(cart);
  document.getElementById("checkout-form").submit();
}  



 