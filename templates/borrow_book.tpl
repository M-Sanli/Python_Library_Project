
% rebase('templates/base.tpl', title="Library")
% include('templates/navigation_bar.tpl', page="borrow_book")

<div class="container">
    <h1 class="text-primary text-center">{{book.title}}</h1>
    <img src="{{book.image_url}}" class="mx-auto d-block" alt="{{'%s image' % book.title}}">
    <p class="text-center mt-3">Congratulations, you have borrowed this book.</p>
    <p class="text-center"> You have <span class="text-info">{{allowed_borrowed_days}}</span> days to return it.</p>
</div>