<!--
The home page of our online library service.

They all rebase "base.tpl" so that we don't have to include
the same HTML code in all templates (<head>, Bootstrap, etc)

See https://bottlepy.org/docs/dev/stpl.html#stpl.rebase
-->
% rebase('templates/base.tpl', title="Library")
% include('templates/navigation_bar.tpl', page="home")
% if not user.borrowed_books:
    <div class="container vh-100 d-flex align-items-center">
        <div class="mx-auto">
            <h5 class="text-info mb-5 text-center">You haven't borrowed any books.</h5>
        </div>
    </div>

% end
<div class="container">
    <h1 class="text-primary text-center">Your Borrowed books</h1>
    <div class="d-flex flex-row flex-wrap bd-highlight">
        % for book in user.borrowed_books:
            % book.author_list = ", ".join([author.name for author in book.authors])
            % include("templates/book.tpl", book=book, card_type="borrowed")
        % end
    </div>
</div>