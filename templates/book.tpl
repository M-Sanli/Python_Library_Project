<div class="card m-2" style="width: 17rem;">
    <img src="{{book.image_url}}" class="card-img-top w-100" alt="{{'%s image' % book.title}}" style="height:25rem;object-fit:cover">
    <div class="card-body">
        <h5 class="card-title">{{book.title}}</h5>
        <p class="card-text">
        <div>
            <span class="text-primary">Authors: </span><span>{{book.author_list}}</span>
        </div>
        <div>
            <span class="text-primary">Year: </span><span>{{book.publication_year}}</span>
        </div>
        <div>
            <span class="text-primary">Rating: </span>
            <span>
                % for _ in range(int(book.average_rating)):
                    <i class="fas fa-star text-warning"></i>
                % end
                % for _ in range(int(book.average_rating), 5):
                    <i class="far fa-star text-warning"></i>
                % end
            </span>
        </div>
        <div>
            <span class="text-primary">Votes: </span><span>{{book.ratings_count}}</span>
        </div>
        </p>
    </div>
    <div class="mx-auto mb-3">
        % if card_type == "to_borrow":
            % if not book.borrowed_by:
                <a href="/borrow_book/{{book.id}}" class="btn btn-primary">Borrow</a>
            % else:
                <span class="text-danger">Book not available until {{book.return_date()}}</span>
            % end
        % else:
            % if book.return_date() > today:
                <p class="text-info">Return it before {{book.return_date()}}</p>
            % else:
                <p class="text-danger">
                    You had to return the book {{book.return_date()}}
                    Please return ASAP.
                </p>
            % end
            <a href="/return_book/{{book.id}}" class="btn btn-primary d-block">Return</a>
        % end
    </div>
</div>